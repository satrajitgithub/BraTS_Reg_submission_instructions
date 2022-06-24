import argparse
import os
import nibabel as nib
import glob
import torch

# *** Disclaimer: Please note that functions like loadmodel, calculate_landmark, write, read, calculate_jacobian, apply_field_on_image etc. are not actual functions and
# used as placeholders for explanatory purposes.

def generate_output(args):
    '''
    Generates landmarks, detJ, deformation fields (optional), and followup_registered_to_baseline images (optional) for challenge submission
    '''
    print("generate_output called")

    input_path = os.path.abspath(args["input"])
    output_path = os.path.abspath(args["output"])

    print(f"* Found following data in the input path {input_path}=", os.listdir(input_path)) # Found following data in the input path /input= ['BraTSReg_001', 'BraTSReg_002']
    print("* Output will be written to=", output_path) # Output will be written to= /output

    # Now we iterate through each subject folder under input_path
    for subj_path in glob.glob(os.path.join(input_path, "BraTSReg*")):
      subj = os.path.basename(subj_path)
      print(f"Now performing registration on {subj}") # Now performing registration on BraTSReg_001

      # Read in your data
      input_df = nib.load(os.path.join(subj_path, f"{subj}_00_0000_t1ce.nii.gz")).get_fdata()

      print(input_df.shape) # (240, 240, 155)

      # Read in your trained model
      model = loadmodel("/usr/local/bin/model.hdf5")

      # Make your prediction segmentation file for case BraTSReg_001

      ## 1. calculate the output landmark points
      output_landmark = calculate_landmark(model, input_df)

      ## write your output_landmark to the output folder as BraTSReg_001.csv
      write(output_landmark, os.path.join(args["output"], f"{subj}.csv"))

      ## 2. calculate the determinant of jacobian of the deformation field
      output_detj = calculate_jacobian(model, input_df)

      ## write your output_detj to the output folder as BraTSReg_001.nii.gz
      write(output_detj, os.path.join(args["output"], f"{subj}_detj.nii.gz"))

      if args["def"]:
          # write both the forward and backward deformation fields to the output/ folder
          print("--def flag is set to True")
          # write(output_def_followup_to_baseline, os.path.join(args["output"], f"{subj}_df_f2b.nii.gz"))
          # write(output_def_baseline_to_followup, os.path.join(args["output"], f"{subj}_df_b2f.nii.gz"))

      if args["reg"]:
          # write the followup_registered_to_baseline sequences (all 4 sequences provided) to the output/ folder
          print("--reg flag is set to True")
          # write(output_followup_to_baseline_t1ce, os.path.join(args["output"], f"{subj}_t1ce_f2b.nii.gz"))
          # write(output_followup_to_baseline_t1, os.path.join(args["output"], f"{subj}_t1_f2b.nii.gz"))
          # write(output_followup_to_baseline_t2, os.path.join(args["output"], f"{subj}_t2_f2b.nii.gz"))
          # write(output_followup_to_baseline_flair, os.path.join(args["output"], f"{subj}_flair_f2b.nii.gz"))


def apply_deformation(args):
    '''
    Applies a deformation field on an input image and saves/returns the output
    '''
    print("apply_deformation called")
        
    # Read the field
    f = read(path_to_deformation_field)

    # Read the input image
    i = read(path_to_input_image)

    # apply field on image and get output
    o = apply_field_on_image(f,i,interpolation_type)

    # If a save_path is provided then write the output there, otherwise return the output
    if save_path:
      write(o, savepath)
    else:
      return o


if __name__ == "__main__":
    # You can first check what devices are available to the singularity
    # setting device on GPU if available, else CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)

    #Additional Info when using cuda
    if device.type == 'cuda':
        print('GPU:', torch.cuda.get_device_name(0))

    # Parse the input arguments

    parser = argparse.ArgumentParser(description='Argument parser for BraTS_Reg challenge')
    
    subparsers = parser.add_subparsers()

    command1_parser = subparsers.add_parser('generate_output')
    command1_parser.set_defaults(func=generate_output)
    command1_parser.add_argument('-i', '--input', type=str, default="/input", help='Provide full path to directory that contains input data')
    command1_parser.add_argument('-o', '--output', type=str, default="/output", help='Provide full path to directory where output will be written')
    command1_parser.add_argument('-d', '--def', action='store_true', help='Output forward and backward deformation fields')
    command1_parser.add_argument('-r', '--reg', action='store_true', help='Output followup scans registered to baseline')

    command2_parser = subparsers.add_parser('apply_deformation')
    command2_parser.set_defaults(func=apply_deformation)
    command2_parser.add_argument('-f', '--field', type=str, required=True, help='Provide full path to deformation field')
    command2_parser.add_argument('-i', '--image', type=str, required=True, help='Provide full path to image on which field will be applied')
    command2_parser.add_argument('-t', '--interpolation', type=str, required=True, help='Should be nearest_neighbour (for segmentation mask type images) or trilinear etc. (for normal scans). To be handled inside apply_deformation() function')
    command2_parser.add_argument('-p', '--path_to_output_nifti', type=str, default = None, help='Format: /path/to/output_image_after_applying_deformation_field.nii.gz')
    

    args = vars(parser.parse_args())

    print("* Received the following arguments =", args) 

    args["func"](args)