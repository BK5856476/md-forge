import os
import subprocess
import sys

def run_skill(skill_path):
    """Execute all .bat scripts inside a skill directory.
    Returns True if all scripts succeed, False otherwise.
    """
    skill_name = os.path.basename(skill_path)
    print(f"\n{'=' * 60}\n📦 Executing Skill: {skill_name}\n{'=' * 60}")

    # Find any .bat files in the skill folder
    bat_files = [f for f in os.listdir(skill_path) if f.lower().endswith('.bat')]
    if not bat_files:
        print(f"[WARN] No .bat runner found in {skill_name}. Skipping.")
        return True  # nothing to run, not a failure

    success = True
    for bat in bat_files:
        print(f"[INFO] Launching {bat} in {skill_name}...")
        print('-' * 40)
        try:
            # Execute the batch file; shell=True lets Windows handle .bat correctly
            subprocess.run([bat], shell=True, cwd=skill_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] {skill_name} failed (exit code {e.returncode}).")
            success = False
        except Exception as e:
            print(f"[ERROR] Unexpected error while running {bat}: {e}")
            success = False
        print('-' * 40)
    return success

def main():
    # Repository root (where this script resides)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.join(root_dir, "skills")

    if not os.path.isdir(skills_dir):
        print(f"❌ Error: 'skills' directory not found at {skills_dir}")
        sys.exit(1)

    # Discover all skill subfolders
    skill_paths = [os.path.join(skills_dir, d) for d in os.listdir(skills_dir)
                   if os.path.isdir(os.path.join(skills_dir, d))]

    if not skill_paths:
        print("ℹ️ No skills found in the 'skills' folder.")
        sys.exit(0)

    print(f"🚀 MDForge: Detected {len(skill_paths)} skill(s). Starting sequential execution...\n")
    overall_success = True
    for sp in skill_paths:
        if not run_skill(sp):
            overall_success = False

    print(f"\n{'=' * 60}")
    if overall_success:
        print("🎉 All skills completed successfully!")
    else:
        print("⚠️ Some skills encountered errors. Review the logs above.")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    main()
