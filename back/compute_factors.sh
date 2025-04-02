#!/bin/bash

# Configuration
input_file="insee.txt"      # File containing the INSEE codes
task_command="python manage.py c04_compute_factors --delete --insee_code_city" # Base task command
num_parallel_tasks=4       # Number of parallel tasks

# Function to process INSEE codes
process_insee_code() {
    local insee_code=$1
    $task_command "$insee_code"
}

# Export function for parallel execution
export -f process_insee_code
export task_command
mkdir -p output

# Run tasks with parallel, limiting concurrency
parallel -j $num_parallel_tasks "$task_command {} > output/{}.log 2>&1" < "$input_file"


# Wait for all tasks to complete
wait
