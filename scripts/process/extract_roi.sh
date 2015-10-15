#!/bin/bash

while getopts ":i:m:o:" opt; do
  case $opt in
    i)
      in_img=$OPTARG
      ;;
    m)
      mask_img=$OPTARG
      ;;
    o)
      out_txt=$OPTARG
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

fslmeants -i "$in_img" -m "$mask_img" >> "$out_txt"
