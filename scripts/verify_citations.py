#!/usr/bin/env python3
"""
Citation Verification Script (80/20 Solution)

Catches fabricated citations by checking:
1. DOI resolution (via doi.org)
2. Basic metadata matching (title similarity, year match)
3. Flags suspicious entries for manual review

Usage:
    python verify_citations.py --report [path]

Does NOT require API keys - uses free DOI resolver and heuristics.
"""

import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple
from urllib import request, error
from urllib.parse import quote
import json
import time

class CitationVerifier:
    """Verify citations in research report"""

    def __init__(self, report_path: Path):
        self.report_path = report_path
        self.content = self._read_report()
        self.suspicious = []
        self.verified = []
        self.errors = []

    def _read_report(self) -> str:
        """Read report file"""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"L ERROR: Cannot read report: {e}")
            sys.exit(1)

    def extract_bibliography(self) -> List[Dict]:
        """Extract bibliography entries from report"""
        pattern = r'## Bibliography(.*?)(?=##|\Z)'
        match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)

        if not match:
            self.errors.append("No Bibliography section found")
            return []

        bib_section = match.group(1)

        # Parse entries: [N] Author (Year). "Title". Venue. URL
        entries = []
        lines = bib_section.strip().split('\n')

        current_entry = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if starts with citation number [N]
            match_num = re.match(r'^\[(\d+)\]\s+(.+)$', line)
            if match_num:
                if current_entry:
                    entries.append(current_entry)

                num = match_num.group(1)
                rest = match_num.group(2)

                # Try to parse: Author (Year). "Title". Venue. URL
                year_match = re.search(r'\((\d{4})\)', rest)
                title_match = re.search(r'"([^"]+)"', rest)
                doi_match = re.search(r'doi\.org/(10\.\S+)', rest)
                url_match = re.search(r'https?://[^\s\)]+', rest)

                current_entry = {
                    'num': num,
                    'raw': rest,
                    'year': year_match.group(1) if year_match else None,
                    'title': title_match.group(1) if title_match else None,
                    'doi': doi_match.group(1) if doi_match else None,
                    'url': url_match.group(0) if url_match else None
                }
            elif current_entry:
                # Multi-line entry, append to raw
                current_entry['raw'] += ' ' + line

        if current_entry:
            entries.append(current_entry)

        return entries

    def verify_doi(self, doi: str) -> Tuple[bool, Dict]:
        """
        Verify DOI exists and get metadata.
        Returns (success, metadata_dict)
        """
        if not doi:
            return False, {}

        try:
            # Use content negotiation to get JSON metadata
            url = f"https://doi.org/{quote(doi)}"
            req = request.Request(url)
            req.add_header('Accept', 'application/vnd.citationstyles.csl+json')

            with request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

                return True, {
                    'title': data.get('title', ''),
                    'year': data.get('issued', {}).get('date-parts', [[None]])[0][0],
                    'authors': [
                        f"{a.get('family', '')} {a.get('given', '')}"
                        for a in data.get('author', [])
                    ],
                    'venue': data.get('container-title', '')
                }
        except error.HTTPError as e:
            if e.code == 404:
                return False, {'error': 'DOI not found (404)'}
            return False, {'error': f'HTTP {e.code}'}
        except Exception as e:
            return False, {'error': str(e)}

    def check_title_similarity(self, title1: str, title2: str) -> float:
        """
        Simple title similarity check (word overlap).
        Returns score 0.0-1.0
        """
        if not title1 or not title2:
            return 0.0

        # Normalize: lowercase, remove punctuation, split
        def normalize(s):
            s = s.lower()
            s = re.sub(r'[^\w\s]', ' ', s)
            return set(s.split())

        words1 = normalize(title1)
        words2 = normalize(title2)

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2)
        total = len(words1 | words2)

        return overlap / total if total > 0 else 0.0

    def verify_entry(self, entry: Dict) -> Dict:
        """Verify a single bibliography entry"""
        result = {
            'num': entry['num'],
            'status': 'unknown',
            'issues': [],
            'metadata': {}
        }

        # Check 1: Has DOI?
        if entry['doi']:
            print(f"  [{entry['num']}] Checking DOI {entry['doi']}...", end=' ')
            success, metadata = self.verify_doi(entry['doi'])

            if success:
                result['metadata'] = metadata
                result['status'] = 'verified'
                print("")

                # Check title similarity if we have both
                if entry['title'] and metadata.get('title'):
                    similarity = self.check_title_similarity(
                        entry['title'],
                        metadata['title']
                    )

                    if similarity < 0.5:
                        result['issues'].append(
                            f"Title mismatch (similarity: {similarity:.1%})"
                        )
                        result['status'] = 'suspicious'

                # Check year match
                if entry['year'] and metadata.get('year'):
                    if int(entry['year']) != int(metadata['year']):
                        result['issues'].append(
                            f"Year mismatch: report says {entry['year']}, DOI says {metadata['year']}"
                        )
                        result['status'] = 'suspicious'

            else:
                print(f"L {metadata.get('error', 'Failed')}")
                result['status'] = 'unverified'
                result['issues'].append(f"DOI resolution failed: {metadata.get('error', 'unknown')}")

        else:
            # No DOI - check for red flags
            result['status'] = 'no_doi'
            result['issues'].append("No DOI provided")

            # Red flag: Very recent year (2024-2025) without DOI is suspicious
            if entry['year'] and int(entry['year']) >= 2024:
                result['issues'].append("Recent publication (2024+) without DOI - may be fabricated")
                result['status'] = 'suspicious'

            # Red flag: No URL at all
            if not entry['url']:
                result['issues'].append("No URL or DOI - cannot verify")
                result['status'] = 'suspicious'

        return result

    def verify_all(self):
        """Verify all bibliography entries"""
        print(f"\n{'='*60}")
        print(f"CITATION VERIFICATION: {self.report_path.name}")
        print(f"{'='*60}\n")

        entries = self.extract_bibliography()

        if not entries:
            print("L No bibliography entries found\n")
            return False

        print(f"Found {len(entries)} citations\n")

        results = []
        for entry in entries:
            result = self.verify_entry(entry)
            results.append(result)

            # Rate limiting
            time.sleep(0.5)

        # Summarize
        print(f"\n{'='*60}")
        print(f"VERIFICATION SUMMARY")
        print(f"{'='*60}\n")

        verified = [r for r in results if r['status'] == 'verified']
        suspicious = [r for r in results if r['status'] == 'suspicious']
        unverified = [r for r in results if r['status'] in ['unverified', 'no_doi', 'unknown']]

        print(f" Verified: {len(verified)}/{len(results)}")
        print(f"   Suspicious: {len(suspicious)}/{len(results)}")
        print(f"S Unverified: {len(unverified)}/{len(results)}")
        print()

        if suspicious:
            print("   SUSPICIOUS CITATIONS (Manual Review Needed):")
            for r in suspicious:
                print(f"\n  [{r['num']}]")
                for issue in r['issues']:
                    print(f"    " {issue}")
            print()

        if unverified and len(unverified) > 0:
            print("S UNVERIFIED CITATIONS (Could not check):")
            for r in unverified:
                print(f"  [{r['num']}] {r['issues'][0] if r['issues'] else 'Unknown'}")
            print()

        # Decision
        if suspicious:
            print("L REVIEW REQUIRED: Suspicious citations detected")
            return False
        elif len(verified) / len(results) < 0.5:
            print("   WARNING: Less than 50% citations verified")
            return True  # Pass with warning
        else:
            print(" CITATION VERIFICATION PASSED")
            return True

def main():
    parser = argparse.ArgumentParser(
        description="Verify citations in research report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_citations.py --report report.md

Note: Requires internet connection to check DOIs.
Uses free DOI resolver - no API key needed.
        """
    )

    parser.add_argument(
        '--report', '-r',
        type=str,
        required=True,
        help='Path to research report markdown file'
    )

    args = parser.parse_args()
    report_path = Path(args.report)

    if not report_path.exists():
        print(f"L ERROR: Report file not found: {report_path}")
        sys.exit(1)

    verifier = CitationVerifier(report_path)
    passed = verifier.verify_all()

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
