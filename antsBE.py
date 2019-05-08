import argparse
from skull_strip import SkullStripper
import os

def get_brain_mask(input_path, output_path, patient_id,atlas_file_path,clean_useless):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    s2 = SkullStripper(input_path=input_path, output_path=output_path, patient_id = patient_id,
                       atlas_file_path = atlas_file_path,clean_useless = clean_useless)
    s2.skull_strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='skull strip with antspy')
    parser.add_argument("input",type=str,help="brain MRI with skull, LGG-123.nii or  LGG-123.nii.gz")
    parser.add_argument("output", type=str, help="output folder name")
    parser.add_argument("--patient_id", type=str, default=None, help='set patient id (optional)')
    parser.add_argument("--atlas_file_path",type = str, default=None, help = 'altas file path,eg. .\\Atlas\\ (optional)')
    parser.add_argument("--clean_useless", type=str, default=False, help='False OR True. if True, delete useless file. (optional)')

    args = parser.parse_args()
    print(args)
    get_brain_mask(input_path = args.input, output_path = args.output, patient_id = args.patient_id,
                   atlas_file_path = args.atlas_file_path, clean_useless= args.clean_useless)


