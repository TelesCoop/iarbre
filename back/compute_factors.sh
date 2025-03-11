#!/bin/bash

input_file="insee.txt"
task_command="python manage.py c04_compute_factors --delete --insee_code_city"
num_parallel_tasks=7

mkdir -p output

run_job() {
    local insee_code=$1
    echo "Starting job for INSEE code: $insee_code"
    $task_command "$insee_code" > "output/${insee_code}.log" 2>&1 &
    echo "Job started with PID: $!"
}

job_count=0
while IFS= read -r insee_code; do
    run_job "$insee_code"
    ((job_count++))
    if [ $job_count -ge $num_parallel_tasks ]; then
        wait -n
        ((job_count--))
    fi
done < "$input_file"

echo "Waiting for all remaining jobs to finish..."
wait
echo "All jobs completed."
