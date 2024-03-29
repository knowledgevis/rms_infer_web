#!/usr/bin/env python
# -*- coding: utf-8 -*-


from arbor_nova_tasks.arbor_tasks.fnlcr import infer_rhabdo 
from arbor_nova_tasks.arbor_tasks.fnlcr import infer_wsi 
from arbor_nova_tasks.arbor_tasks.fnlcr import infer_rms_map
from arbor_nova_tasks.arbor_tasks.fnlcr import wsi_thumbnail
from arbor_nova_tasks.arbor_tasks.fnlcr import myod1 
from arbor_nova_tasks.arbor_tasks.fnlcr import survivability 
from arbor_nova_tasks.arbor_tasks.fnlcr import cohort 

from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import filtermodel, Resource
from girder_worker_utils.transforms.girder_io import GirderFileId, GirderUploadToItem
from girder_worker_utils.transforms.contrib.girder_io import GirderFileIdAllowDirect


class ArborNova(Resource):
    def __init__(self):
        super(ArborNova, self).__init__()
        self.resourceName = 'arbor_nova'
        self.route('POST', ('infer_rhabdo', ), self.infer_rhabdo)
        self.route('POST', ('infer_wsi', ), self.infer_wsi)
        self.route('POST', ('infer_rms_map', ), self.infer_rms_map)
        self.route('POST', ('wsi_thumbnail', ), self.wsi_thumbnail)
        self.route('POST', ('myod1', ), self.myod1)
        self.route('POST', ('survivability', ), self.survivability)
        self.route('POST', ('cohort', ), self.cohort)
    @access.token
    @filtermodel(model='job', plugin='jobs')



# ---DNN infer command line for FNLCR
    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
        Description('perform forward inferencing using a pretrained network')
        .param('imageId', 'The ID of the source, a TIF image file.')
        .param('outputId', 'The ID of the output item where the output file will be uploaded.')
        .param('statsId', 'The ID of the output item where the output file will be uploaded.')
        .errorResponse()
        .errorResponse('Write access was denied on the parent item.', 403)
        .errorResponse('Failed to upload output file.', 500)
    )
    def infer_rhabdo(
            self, 
            imageId, 
            outputId,
            statsId
    ):
        result = infer_rhabdo.delay(
                #GirderFileId(imageId), 
                GirderFileIdAllowDirect(imageId), 
                girder_result_hooks=[
                    GirderUploadToItem(outputId),
                    GirderUploadToItem(statsId),

                ])
        return result.job

    # ---DNN infer command line for FNLCR
    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
        Description('perform forward inferencing using a pretrained network')
        .param('imageId', 'The ID of the source, an Aperio .SVS image file.')
        .param('outputId', 'The ID of the output item where the output file will be uploaded.')
        .param('statsId', 'The ID of the output item where the output file will be uploaded.')
        .errorResponse()
        .errorResponse('Write access was denied on the parent item.', 403)
        .errorResponse('Failed to upload output file.', 500)
    )
    def infer_wsi(
            self, 
            imageId, 
            outputId,
            statsId
    ):
        result = infer_wsi.delay(
                #GirderFileId(imageId), 
                GirderFileIdAllowDirect(imageId), 
                girder_result_hooks=[
                    GirderUploadToItem(outputId),
                    GirderUploadToItem(statsId),
                ]
                )
        return result.job


    # ---cancer map version of segmentation method
    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
        Description('perform forward inferencing using a pretrained network')
        .param('imageId', 'The ID of the source, an Aperio .SVS image file.')
        .param('outputId', 'The ID of the output item where the output file will be uploaded.')
        .param('statsId', 'The ID of the output item where the output file will be uploaded.')
        .errorResponse()
        .errorResponse('Write access was denied on the parent item.', 403)
        .errorResponse('Failed to upload output file.', 500)
    )
    def infer_rms_map(
            self, 
            imageId, 
            outputId,
            statsId
    ):
        result = infer_rms_map.delay(
                #GirderFileId(imageId), 
                GirderFileIdAllowDirect(imageId),               
                girder_result_hooks=[
                    GirderUploadToItem(outputId),
                    GirderUploadToItem(statsId),
                ]
                )
        return result.job



    # --- generate a thumbnail from a pyramidal image
    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
        Description('generate a wsi_thumbnail')
        .param('imageId', 'The ID of the source, an Aperio .SVS image file.')
        .param('outputId', 'The ID of the output item where the output file will be uploaded.')
        .errorResponse()
        .errorResponse('Write access was denied on the parent item.', 403)
        .errorResponse('Failed to upload output file.', 500)
    )
    def wsi_thumbnail(
            self, 
            imageId, 
            outputId
    ):
        result = wsi_thumbnail.delay(
                #GirderFileId(imageId), 
                GirderFileIdAllowDirect(imageId), 
                girder_result_hooks=[
                    GirderUploadToItem(outputId)
                ])
        return result.job

     # --- DNN myod1 model inference.  This is a classification model from FNLCR
     # --- that produces a probability of MYOD1 mutation
    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
        Description('perform classification through forward inferencing using a pretrained network')
        .param('imageId', 'The ID of the source, an Aperio .SVS image file.')
        .param('segmentId', 'The ID of the segmentation image, a PNG or TIFF image.')
         .param('statsId', 'The ID of the output item where the output file will be uploaded.')
        .errorResponse()
        .errorResponse('Write access was denied on the parent item.', 403)
        .errorResponse('Failed to upload output file.', 500)
    )
    def myod1(
            self, 
            imageId, 
            segmentId,
            statsId
    ):
        result = myod1.delay(
                #GirderFileId(imageId), 
                GirderFileIdAllowDirect(imageId), 
                #GirderFileId(segmentId), 
                GirderFileIdAllowDirect(segmentId), 
                girder_result_hooks=[
                    GirderUploadToItem(statsId),
                ])
        return result.job

     # --- DNN survivability model inference.  This is a classification model from FNLCR
     # --- that produces a classification of low-to-high risk for survivability prediction
    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
        Description('perform classification through forward inferencing using a pretrained network')
        .param('imageId', 'The ID of the source, an Aperio .SVS image file.')
        .param('segmentId', 'The ID of the segmentation image, a PNG or TIFF image.')
        .param('fastmode', 'a binary flag indicating user desire to return a faster, approximate solution')
        .param('statsId', 'The ID of the output item where the output file will be uploaded.')
        .errorResponse()
        .errorResponse('Write access was denied on the parent item.', 403)
        .errorResponse('Failed to upload output file.', 500)
    )
    def survivability(
            self, 
            imageId,
            segmentId,
            fastmode,
            statsId,

    ):
        result = survivability.delay(
                #GirderFileId(imageId), 
                GirderFileIdAllowDirect(imageId), 
                #GirderFileId(segmentId), 
                GirderFileIdAllowDirect(segmentId),
                fastmode, 
                girder_result_hooks=[
                    GirderUploadToItem(statsId),
                ])
        return result.job


     # --- return a cohort of data for use by the display algorithms
    @access.token
    @filtermodel(model='job', plugin='jobs')
    @autoDescribeRoute(
        Description('return a cohort of data')
        .param('cohortName', 'the key to specify which cohort (e.g. "myod1" or "survivability")')
        .param('outnameId', 'The ID of the output item where the data file will be uploaded.')
 
        .errorResponse()
        .errorResponse('Write access was denied on the parent item.', 403)
        .errorResponse('Failed to upload output file.', 500)
    )
    def cohort(
            self, 
            cohortName,
            outnameId
    ):
        result = cohort.delay(
                cohortName, 
                girder_result_hooks=[
                    GirderUploadToItem(outnameId),
                ])
        return result.job
