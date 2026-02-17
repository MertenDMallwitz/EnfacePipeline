
def Distance_Map(impath):
    import numpy as np
    import tifffile as tiff
    import matplotlib.pyplot as plt
    from scipy import ndimage as ndi
    import numpy as np
    from scipy import ndimage as ndi
    import matplotlib.pyplot as plt
    from pathlib import Path
    img = tiff.imread(impath)
    bw = (img > 0)            # make boolean if not already
    structure = np.ones((3,3))
    dil = ndi.binary_dilation(bw, structure=structure)
    er  = ndi.binary_erosion(bw,  structure=structure)
    edges = dil ^ er          # morphological gradient


    plt.imshow(edges, cmap='Reds', alpha=0.6)
    dil = ndi.binary_dilation(bw, structure=structure)
    er  = ndi.binary_erosion(bw,  structure=structure)
    edges = dil ^ er          # morphological gradient
    # guard
    if not np.any(edges):
        raise RuntimeError("No edge pixels found in `edges` mask.")

    # distance (pixels) to nearest edge for every pixel
    dist_to_edge = ndi.distance_transform_edt(~edges)  # edges==True -> zero distance

    # signed distance: positive for background (bw==False), negative for foreground (bw==True)
    signed_dist = dist_to_edge.astype(np.float32) * (np.where(bw, -1.0, 1.0).astype(np.float32))

    # visualize signed distance (blue=negative inside, red=positive outside)
    """maxabs = np.max(np.abs(signed_dist))
    plt.figure(figsize=(6,6))
    plt.imshow(signed_dist, cmap='seismic', vmin=-maxabs, vmax=maxabs)
    plt.colorbar(label='Signed distance (pixels)')
    plt.title('Signed distance to nearest edge (neg inside object)')
    plt.axis('off')
    plt.show()"""
    impath = Path(impath)
    tiff.imwrite(impath.parent / "drusen_edges_768x768.tif", edges.astype('float32'))
    tiff.imwrite(impath.parent / "signed_dist_768x768.tif", signed_dist.astype('float32'))
    