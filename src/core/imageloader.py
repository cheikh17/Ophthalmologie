import vtk

class ImageLoader:
    def load_image_series(self, directory_path):
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(directory_path)
        reader.Update()

        extent = reader.GetDataExtent()

        reslice = vtk.vtkImageReslice()
        reslice.SetInputConnection(reader.GetOutputPort())
        reslice.SetOutputDimensionality(2)
        reslice.SetResliceAxesDirectionCosines([1, 0, 0, 0, 1, 0, 0, 0, 1])
        reslice.SetResliceAxesOrigin(0, 0, 0)
        reslice.Update()

        return reslice, reader, extent

    def get_slice(self, reslice, slice_number):
        # Update the reslice object to get the desired slice
        reslice.SetResliceAxesOrigin(0, 0, slice_number)
        reslice.Update()
        return reslice.GetOutput()