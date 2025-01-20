#!/bin/bash

# Configuration
input_file="insee.txt"      # File containing the INSEE codes
num_groups=5                # Number of groups (can be changed)
task_command="python manage.py c04_compute_factors --insee_code_city" # Base task command

cd back
# Divide the input file into groups
total_lines=$(wc -l < "$input_file")
lines_per_group=$(( (total_lines + num_groups - 1) / num_groups )) # Calculate lines per group, round up
split -l "$lines_per_group" "$input_file" insee_group_

# Launch tasks in parallel
for file in insee_group_*; do
    # Read the codes from the file and join them with commas
    insee_codes=$(paste -sd, "$file")
    echo $insee_codes

    # Run the command in parallel
    $task_command "$insee_codes" &
done

# Wait for all tasks to complete
wait

# Cleanup
rm insee_group_*
