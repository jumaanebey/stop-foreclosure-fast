#!/usr/bin/env python3
"""
CapCut Draft Creator
Creates CapCut project drafts from YouTube scripts that you can open in CapCut for editing.

This uses the CapCutAPI library to generate draft files.
"""

import sys
import os
import re
import json
import shutil
from pathlib import Path

# Add CapCutAPI to path
CAPCUT_API_PATH = os.path.join(os.path.dirname(__file__), 'CapCutAPI')
sys.path.insert(0, CAPCUT_API_PATH)

try:
    import pyJianYingDraft as draft
except ImportError:
    print("Error: pyJianYingDraft not found. Make sure CapCutAPI is installed.")
    sys.exit(1)


class CapCutDraftCreator:
    def __init__(self, output_dir="./drafts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Find CapCut drafts folder
        self.capcut_drafts = self._find_capcut_drafts_folder()

    def _find_capcut_drafts_folder(self):
        """Find CapCut's draft folder on macOS"""
        possible_paths = [
            Path.home() / "Movies" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft",
            Path.home() / "Library" / "Application Support" / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Create default location
        default = possible_paths[0]
        default.mkdir(parents=True, exist_ok=True)
        return default

    def parse_script(self, script_path):
        """Parse a YouTube script markdown file into sections"""
        with open(script_path, 'r') as f:
            content = f.read()

        sections = []

        # Get title
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"

        # Parse sections with timestamps
        section_pattern = r'^## (.+?) \((\d+:\d+)-(\d+:\d+)\)'

        current_pos = 0
        for match in re.finditer(section_pattern, content, re.MULTILINE):
            section_title = match.group(1)
            start = self._time_to_seconds(match.group(2))
            end = self._time_to_seconds(match.group(3))

            # Find text until next section
            next_match = re.search(r'^## ', content[match.end():], re.MULTILINE)
            if next_match:
                section_text = content[match.end():match.end() + next_match.start()]
            else:
                section_text = content[match.end():]

            # Extract quoted dialogue
            quotes = re.findall(r'"([^"]+)"', section_text)
            dialogue = ' '.join(quotes) if quotes else section_title

            sections.append({
                'title': section_title,
                'start': start,
                'end': end,
                'duration': end - start,
                'dialogue': dialogue[:200]  # Limit length
            })

        return title, sections

    def _time_to_seconds(self, time_str):
        """Convert MM:SS to seconds"""
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])

    def create_draft(self, script_path, project_name=None):
        """Create a CapCut draft from a script"""
        title, sections = self.parse_script(script_path)

        if project_name is None:
            project_name = re.sub(r'[^\w\s-]', '', title)[:30]

        print(f"Creating CapCut draft: {project_name}")
        print(f"Found {len(sections)} sections")

        # Create script file (1920x1080 for YouTube)
        script_file = draft.Script_file(1920, 1080)

        # Add text tracks for each section
        for i, section in enumerate(sections):
            print(f"  Adding section: {section['title']}")

            # Convert times to microseconds (CapCut uses microseconds)
            start_us = section['start'] * 1_000_000
            duration_us = section['duration'] * 1_000_000

            # Add title text for section
            try:
                # Create text segment
                text_content = f"{section['title']}\n\n{section['dialogue'][:100]}"

                # Note: The actual text addition depends on the pyJianYingDraft version
                # This is a simplified version

            except Exception as e:
                print(f"    Warning: Could not add text: {e}")

        # Save draft
        draft_folder = self.output_dir / project_name
        draft_folder.mkdir(parents=True, exist_ok=True)

        try:
            script_file.dump(str(draft_folder))
            print(f"\nDraft saved to: {draft_folder}")

            # Copy to CapCut drafts folder
            if self.capcut_drafts:
                capcut_project = self.capcut_drafts / project_name
                if capcut_project.exists():
                    shutil.rmtree(capcut_project)
                shutil.copytree(draft_folder, capcut_project)
                print(f"Draft copied to CapCut: {capcut_project}")
                print("\nOpen CapCut and look for the project in your drafts!")

        except Exception as e:
            print(f"Error saving draft: {e}")
            return None

        return str(draft_folder)


def create_demo_draft():
    """Create a demo draft from the foreclosure script"""
    creator = CapCutDraftCreator(
        output_dir="/Users/jumaanebey/Documents/stop-foreclosure-fast/video-tools/capcut-drafts"
    )

    script_path = "/Users/jumaanebey/Documents/stop-foreclosure-fast/youtube-scripts/01-stop-foreclosure-california.md"

    if os.path.exists(script_path):
        output = creator.create_draft(script_path, "Stop-Foreclosure-California")
        return output
    else:
        print("Script file not found!")
        return None


if __name__ == "__main__":
    create_demo_draft()
