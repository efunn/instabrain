#!/bin/bash

while getopts ":r:a:i:o:" opt; do
  case $opt in
    r)
      roi_name=$OPTARG
      ;;
    a)
      atlas_dir=$OPTARG
      ;;
    i)
      atlas_img=$OPTARG
      ;;
    o)
      outfile_img=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

atlas_index=$(grep "$roi_name" "$atlas_dir" | cut -f2-2 -d\")
fslroi "$atlas_img" "$outfile_img" "$atlas_index" 1