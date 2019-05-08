import ants
import numpy as np
import nibabel as nib
import os
from nilearn.image import math_img, threshold_img
import argparse
from ants import utils
import glob

class SkullStripper():
    def __init__(self,input_path,output_path,patient_id = None, atlas_file_path = None, clean_useless = False):
        self.input_path = input_path
        self.output_path = output_path
        self.clean = clean_useless

        if patient_id:
            self.patient_id = patient_id
        else:
            self.patient_id = os.path.splitext(os.path.splitext(os.path.basename(input_path))[0])[0]

        if atlas_file_path:
            self.moving_img_path_t1 = atlas_file_path + '\\atlas_t1.nii'
            self.moving_img_path_mask = atlas_file_path + '\\atlas_mask.nii'
        else:
            self.moving_img_path_t1 = '.\\Atlas\\atlas_t1.nii'
            self.moving_img_path_mask = '.\\Atlas\\atlas_mask.nii'

        self.transforms = None

    def compute_registration(self):
        imgs = self.input_path + ',' + self.moving_img_path_t1
        outprefix = self.output_path + self.patient_id + '_atlas_reg'
        args = ['-d', '3',
                '-r', '[' + imgs + ',1]',
                '-t', 'Translation[0.1]',
                '-m', 'mattes[' + imgs + ',1,32,regular,0.05]',
                '-c', '[1000, 1e-8, 20]',
                '-s', '4vox',
                '-f', '6',
                '-l', '1',
                '-t', 'Rigid[0.1]',
                '-m', 'mattes[' + imgs + ',1,32,regular,0.1]',
                '-c', '[1000x1000,1e-8,20]',
                '-s', '4x2vox',
                '-f', '4x2',
                '-l', '1',
                '-t', 'Affine[0.1]',
                '-m', 'mattes[' + imgs + ',1,32,regular,0.1]',
                '-c', '[10000x1111x5,1e-8,20]',
                '-s', '4x2x1vox',
                '-f', '3x2x1',
                '-l', '1',
                '-o', outprefix]
        processed_args = utils._int_antsProcessArguments(args)
        libfn = utils.get_lib_fn('antsRegistration')
        libfn(processed_args)
        alltx = sorted(glob.glob(outprefix + '*' + '[0-9]*'))
        fwdtransforms = list(reversed(alltx))
        self.transforms = fwdtransforms[0]
        return fwdtransforms[0]

    def apply_transforms(self,target):
        """
        :param target: '_atlas_reg.nii.gz' or '_premask.nii.gz'
        :return:
        """
        if target == '_atlas_reg.nii.gz':
            moving_img_path = self.moving_img_path_t1
        elif target == '_premask.nii.gz':
            moving_img_path = self.moving_img_path_mask
        else:
            print('target error')

        outprefix = self.output_path + self.patient_id + target
        mytx = ['-t', self.transforms]
        args = ['-d', 3,
                '-i', moving_img_path,
                '-o', outprefix,
                '-r', self.input_path]
        args = args + mytx
        myargs = utils._int_antsProcessArguments(args)
        for jj in range(len(myargs)):
            if myargs[jj] is not None:
                if myargs[jj] == '-':
                    myargs2 = [None] * (len(myargs) - 1)
                    myargs2[:(jj - 1)] = myargs[:(jj - 1)]
                    myargs2[jj:(len(myargs) - 1)] = myargs[(jj + 1):(len(myargs))]
                    myargs = myargs2

        processed_args = myargs + ['-z', str(1),  '--float', str(1)]
        libfn = utils.get_lib_fn('antsApplyTransforms')
        libfn(processed_args)

        return outprefix


    def skull_strip(self):
        img_nii = nib.load(self.input_path)
        affine = img_nii.affine
        affine_mat_path = self.compute_registration()
        atlas_reg_file_path = self.apply_transforms(target='_atlas_reg.nii.gz')
        pre_mask_file_path = self.apply_transforms(target='_premask.nii.gz')

        mask = nib.load(pre_mask_file_path)
        mask = math_img("img > 0.9", img=mask)

        mask_data = mask.get_data()
        mask_nii = nib.Nifti1Image(mask_data, affine)
        mask_nii.to_filename(self.output_path + self.patient_id + '_mask.nii.gz')

        if self.clean:
            print("remove ",affine_mat_path)
            os.remove(affine_mat_path)
            print("remove ",atlas_reg_file_path)
            os.remove(atlas_reg_file_path)
            print("remove ",pre_mask_file_path)
            os.remove(pre_mask_file_path)



if __name__ == '__main__':
    output_path = '.\\output\\'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    input_path = 'LGG-104_T1.nii.gz'

    s2 = SkullStripper(input_path = input_path, output_path = output_path)
    s2.skull_strip()












