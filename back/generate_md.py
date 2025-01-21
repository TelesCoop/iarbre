import os

# Path to the directory containing the Python scripts
scripts_dir = "api/utils"

# Path to the output directory for the .md files
output_dir = "docs/api"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Loop through all files in the scripts directory
for filename in os.listdir(scripts_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]  # Remove the '.py' extension
        md_filename = f"{module_name}.md"  # Corresponding .md file
        md_filepath = os.path.join(output_dir, md_filename)

        # Write the content to the .md file
        with open(md_filepath, "w") as md_file:
            md_file.write(f"# {module_name.replace('_', ' ').title()}\n\n")
            md_file.write(f"::: api.utils.{module_name}\n")

        print(f"Generated {md_filepath}")
