import scipy.ndimage as nd
import scipy.misc as misc

from imreg import register, model, metric
from imreg.samplers import sampler

# Form some test data (lena, lena rotated 20 degrees)
image = misc.lena()
template = nd.rotate(image, 20, reshape=False)

# Form the affine registration instance.
affine = register.Register(
         model.Affine,
         metric.Residual,
         sampler.CubicConvolution
         )

# Coerce the image data into RegisterData.
image = register.RegisterData(image).downsample(2)
template = register.RegisterData(template).downsample(2)

# Register.
step, search = affine.register(
                image,
                template,
                verbose=True,

  
# Image pyramid registration can be executed like so:
pHat = None
for factor in [30., 20. , 10., 5., 2., 1.]:
    if pHat is not None:
          scale = downImage.coords.spacing / factor
          # FIXME: Find a nicer way to do this.
          pHat = model.Affine.scale(pHat, scale))

    downImage = image.downsample(factor)
    downTemplate = template.downsample(factor)

    step, search = affine.register(
        downImage,
        downTemplate,
        p=pHat,
        verbose=True
        )

    pHat = step.p

    fullSearch.extend(search)
