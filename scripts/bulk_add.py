import subprocess
from pathlib import Path
import sys


def bulk_add():
    urls_file = Path("./scripts/bulk_urls.txt")
    if not urls_file.exists():
        print(f"Error: {urls_file} not found.")
        sys.exit(1)

    urls = urls_file.read_text().splitlines()
    urls = [u.strip() for u in urls if u.strip() and not u.startswith("#")]

    if not urls:
        print("No URLs found in the file.")
        return

    print(f"Found {len(urls)} URLs. Starting bulk add...")

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")

        # We send a large number of newlines to the process's stdin.
        # This effectively "presses Enter" for every prompt encountered.
        # Since we updated the add command to have defaults for everything,
        # this will accept all extracted or default values.
        try:
            # Using subprocess.Popen to allow real-time output if desired,
            # but subprocess.run with input is simpler for "accepting all defaults".
            result = subprocess.run([sys.executable, "-m", "job_tracker.main", "add", "--url", url], input="\n" * 100, text=True, capture_output=False)  # Plenty of newlines to cover all prompts  # Let it print directly to the terminal

            if result.returncode == 0:
                print(f"Successfully processed {url}")
            else:
                print(f"Finished processing {url} with return code {result.returncode}")

        except Exception as e:
            print(f"Failed to process {url}: {e}")

    print("\nBulk add complete!")


if __name__ == "__main__":
    bulk_add()
