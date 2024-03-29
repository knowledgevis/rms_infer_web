<template>
  <v-app>
    <v-layout class="transform-view" row fill-height>
      <v-navigation-drawer permanent fixed style="width: 400px; min-width: 400px;">
        <v-toolbar dark flat color="primary">
          <v-toolbar-title class="white--text">MYOD1 Mutation Positive/Negative</v-toolbar-title>
          </v-toolbar>
          <v-spacer/>
          <v-container fluid>

          <v-flex xs12>
              <v-btn
              outline
              block
                @click="loadSampleImageFile"
              >
              Use a Pre-Loaded Sample Image
              </v-btn>
            </v-flex>

          <v-flex xs12>
            <v-btn class="text-none" outline block @click='$refs.imageFile.click()'>{{ imageFileName || 'UPLOAD Whole Slide Image' }}</v-btn>
            <input
              type="file"
              style="display: none"
              ref="imageFile"
              @change="uploadImageFile($event.target.files[0])"
            >
          </v-flex>

      <!--    
          <v-flex xs12>
            <v-btn class="text-none" outline block @click='$refs.segmentFile.click()'>{{ segmentFileName || '(optional) UPLOAD Segmentation Mask' }}</v-btn>
            <input
              type="file"
              style="display: none"
              ref="segmentFile"
              @change="uploadSegmentationFile($event.target.files[0])"
            >
          </v-flex>
      -->
          <v-flex xs12>
            <v-btn
              block
              :class="{ primary: readyToRun }"
              :flat="readyToRun"
              :outline="!readyToRun"
              :disabled="!readyToRun"
              @click="run"
            >
              Calculate MyOD1 Mutation
            </v-btn>
          </v-flex>

          <!-- <v-flex xs12>
            <v-btn
              block
              :class="{ primary: readyToDownload }"
              :flat="readyToDownload"
              :outline="!readyToDownload"
              :disabled="!readyToDownload"
              @click="downloadResults"
            >
              Download Results 
            </v-btn>
          </v-flex> -->

          <v-flex xs12>
            <v-btn
              block
              :class="{ primary: readyToDownload }"
              :flat="readyToDownload"
              :outline="!readyToDownload"
              :disabled="!readyToDownload"
              @click="reset"
            >
              Prepare For Another Image 
            </v-btn>
          </v-flex>
        </v-container>
      </v-navigation-drawer>
      <v-layout column justify-start fill-height style="margin-left: 400px">
          <v-card class="ma-4">
            <v-card-text>
              <b>This application analyzes a whole slide image for genetic mutation by executing a neural network that has
                  been pre-trained to predict MYOD1 mutations in rhabdomyosarcoma tissue subtypes in H&E stained   
                  whole slide images.  Uploaded images must in Aperio (.svs) or another similar WSI format.  Large PNG and TIFF files are not supported.
                  <br><br>
                  After selecting an image for upload, be patient during the upload process. Once the input image is displayed below, please click the
                   "Calculate" button to begin execution.  Execution may take up to several minutes,
                  depending on the size of the input image being provided.  When the analysis is complete, the resulting classification and confidence information 
                  will be displayed below and will be available for download.
                  <br><br>
                    Once the chart is displayed showing your uploaded image compared with our cohort, the chart may be downloaded by selecting
                    an option from the "three dots menu" near the top right corner of the chart.  After you are finished reviewing results, 
                    If you would like to classify additional images, please just click "Prepare for Another Image" in between the processing of each image. 
                    This tells the system to reset and prepare to run again.  
                  <br><br>
                    Please attempt this application on a computer system with at least 32GB of memory (as the absolute minumum).  We encourage the use of a recent NVIDIA GPU
                    with at least 12GB of GPU memory and at least 128GB of system memory to process larger images. In our experience, insuffient system memory is the most likely cause if 
                    this application does not finish successfully.   If you are using Docker Desktop application to run this image, it is likely you will need to go into the Resources 
                tab and increase the "Memory Size" to be as large as possible for your particular system (at least 32GB).
                  <br><br>
                  We are delighted that you are trying our early release system for rhabdomyosarcoma analysis.  
                </b>
            </v-card-text>
          </v-card>

        <div v-if="uploadIsHappening" xs12 class="text-xs-center mb-4 ml-4 mr-4">
            Image Upload in process...
            <v-progress-linear :value="progressUpload"></v-progress-linear>
        </div>

       <div v-if="thumbnailInProgress" xs12 class="text-xs-center mb-4 ml-4 mr-4">
            Generating a thumbnail of the uploaded image to display...
            <v-progress-linear indeterminate=True></v-progress-linear>
        </div>

        <div v-if="inputReadyForDisplay">
          <div  xs12 class="text-xs-center mb-4 ml-4 mr-4">
            <v-card class="mb-4 ml-4 mr-4">
              <v-card-text>Uploaded Image</v-card-text>
                <img :src="inputImageUrl" style="display: block; margin: auto"> 
              </v-card>
          </div>
        </div>

       <div v-if="segmentUploadInProgress" xs12 class="text-xs-center mb-4 ml-4 mr-4">
            Preparing Image Segmentation.  This may take several minutes ...
            <v-progress-linear :value="progressSegmentation"></v-progress-linear>
        </div>


        <div v-if="segmentReadyForDisplay">
  	      <v-card class="mb-4 ml-4 mr-4">
            <v-card-text>Segmentation Mask</v-card-text>
               <img :src="segmentImageUrl" width="800" height="600" style="display: block; margin: auto"> 
          </v-card>
        </div>

        <div v-if="running" xs12 class="text-xs-center mb-4 ml-4 mr-4">
          Running MYOD1 Neural network inferencing.  Please wait for the output to show below.  This will take several minutes.
          <v-progress-linear :value="progress"></v-progress-linear>
        </div>
        <div v-if="runCompleted" xs12 class="text-xs-center mb-4 ml-4 mr-4">
          Analysis Complete  ... 
        </div>

        <div v-show="runCompleted">
          <div  xs12 class="text-xs-center mb-4 ml-4 mr-4">
              Below is a chart comparing the MYOD1 mutation level predicted in the tested image when 
              compared to the images in our training cohort.  Click the elipsis icon at the top right 
              to save a copy of the chart to your local system.
          </div>
          <v-card  align="center" justify="center" class="mt-20 mb-4 ml-4 mr-4">
            
            <div id="visM" ref="visModel" class="mt-20 mb-4 ml-4 mr-4"></div>
          </v-card>

          <v-card v-if="table.length > 0" class="mt-8 mb-4 ml-4 mr-4">
            <v-card-text>AI Predicted Score for MYOD1+ Mutation:</v-card-text>
            <json-data-table :data="table" />
          </v-card>
        </div>

        <code v-if="!running && job.status === 4" class="mb-4 ml-4 mr-4" style="width: 100%">{{ job.log.join('\n') }}</code> 
     
      </v-layout>
    </v-layout>
  </v-app>
</template>

<script>

import { utils } from '@girder/components/src';
import { csvParse } from 'd3-dsv';
import scratchFolder from '../scratchFolder';
import pollUntilJobComplete from '../pollUntilJobComplete';
import optionsToParameters from '../optionsToParameters';
import JsonDataTable from '../components/JsonDataTable';
import vegaEmbed from 'vega-embed';
import UploadManager from '../utils/upload'

export default {
  name: 'myod1',
  inject: ['girderRest'],
  components: {
    JsonDataTable,
  },
  data: () => ({
    imageFile: {},
    imageFileName: '',
    segmentFile: {},
    segmentFileName: '',
    imagePointer: '',
    imageBlob: [],
    uploadedImageUrl: '',
    job: { status: 0 },
    readyToDisplayInput: false,
    readyToDisplaySegmentation: false,
    running: false,
    thumbnail: [],
    result: [],
    resultColumns: [],
    resultString:  '',
    runCompleted: false,
    uploadInProgress: false,
    segmentUploadInProgress: false,
    inputImageUrl: '',
    segmentImageUrl: '',
    inputDisplayed:  false,
    segmentDisplayed: false,
    outputDisplayed:  false,
    table: [],
    osd_viewer: [],
    cohortData: [],
    progress: "0",
    progressUpload: "0",
    progressSegmentation: "0",
    segmentationProgressUpload: "0",
  }),
  
  asyncComputed: {
    scratchFolder() {
      return scratchFolder(this.girderRest);
    },
  },
  computed: {
    readyToRun() {
      return !!this.imageFileName && !this.running
    },
    readyToDownload() {
      return (this.runCompleted)
    },
    uploadIsHappening() {
      return (this.uploadInProgress)
    },
    segmentUploadIsHappening() {
      return (this.segmentUploadInProgress)
    },
    inputReadyForDisplay() {
      return this.inputDisplayed
    },
    segmentReadyForDisplay() {
      return this.segmentDisplayed
    }
  },

  methods: {

    // method here to create and display a thumbnail of an arbitrarily large whole slilde image.
    // This code is re-executed for each UI change, so the code is gated to only run once 

    async renderInputImage() {
       if (this.inputDisplayed == false) {
        this.thumbnailInProgress = true
        // create a spot in Girder for the output of the REST call to be placed
          const outputItem = (await this.girderRest.post(
            `item?folderId=${this.scratchFolder._id}&name=thumbnail`,
          )).data

        // build the params to be passed into the REST call
        const params = optionsToParameters({
          imageId: this.imageFile._id,
          outputId: outputItem._id,
        });
        // start the job by passing parameters to the REST call
        this.job = (await this.girderRest.post(
          `arbor_nova/wsi_thumbnail?${params}`,
        )).data;

          // wait for the job to finish
          await pollUntilJobComplete(this.girderRest, this.job, job => this.job = job);

          if (this.job.status === 3) {
            this.running = false;
            // pull the URL of the output from girder when processing is completed. This is used
            // as input to an image on the web interface
            this.thumbnail = (await this.girderRest.get(`item/${outputItem._id}/download`,{responseType:'blob'})).data;
            // set this variable to display the resulting output image on the webpage 
            this.inputImageUrl = window.URL.createObjectURL(this.thumbnail);
            this.thumbnailInProgress = false
          }
          console.log('render input finished')
          // turn off the "upload in process message, since the thumbnail is now finished"
          this.uploadInProgress = false;
	        this.inputDisplayed = true
	     }
    },

   async renderSegmentImage() {
       if (this.segmentDisplayed == false) {
          this.running = false;
          // pull the URL of the output from girder
          this.thumbnail = (await this.girderRest.get(`file/${this.segmentFile._id}/download`,{responseType:'blob'})).data;
          // set this variable to display the resulting output image on the webpage 
          this.segmentImageUrl = window.URL.createObjectURL(this.thumbnail);
          console.log('render segment finished')
          this.segmentDisplayed = true
          this.segmentUploadInProgress = false
	     }
    },


  updateJobStatus(job) {
      this.job = job
      // pick out the last print message from the job

      var last_element = job.log[job.log.length - 1];
      if (last_element) {
          console.log(last_element)
          console.log(last_element.substring(1,9))
          console.log(last_element.substring(9,last_element.length))
          //console.log(progressSnippet.substring(1,9))
          //console.log(progressSnippet.substring(1,2))
          // if this is a progress update string, then extract the percentage done and update the state variable
          if (last_element.substring(1,9)=='progress') {
            // starting at this position, is the string of the value to update the progress bar
            this.progress = last_element.substring(11,last_element.length)
            console.log('percentage:',this.progress)
          }
        }
    },


    async run() {
  
      this.errorLog = null;

      // if there was no segmentation file uploaded, then run segmentation on demand
      if (this.segmentFileName.length == 0) {
        console.log('running segmentation since none was uploaded')
        const result = await this.generateSegmentation()
        console.log('segmentation received')
      } 


      // create a spot in Girder for the output of the REST call to be placed
      const outputItem = (await this.girderRest.post(
        `item?folderId=${this.scratchFolder._id}&name=result`,
      )).data

      // build the params to be passed into the REST call
      var params = optionsToParameters({
        imageId: this.imageFile._id,
        segmentId: this.segmentFile._id,
        statsId: outputItem._id,
      });

      this.running = true
      // start the job by passing parameters to the REST call
      this.job = (await this.girderRest.post(
        `arbor_nova/myod1?${params}`,
      )).data;

      // wait for the job to finish
      await pollUntilJobComplete(this.girderRest, this.job, this.updateJobStatus);

      if (this.job.status === 3) {
        this.running = false;
	      // pull the URL of the output from girder when processing is completed. This is used
	      // as input to an image on the web interface
        this.result = (await this.girderRest.get(`item/${outputItem._id}/download`,{responseType:'text'})).data;
        this.runCompleted = true;
        this.stats = this.result
        console.log('stats:',this.stats)

        // copy this data to a state variable for rendering in a table
        this.data = [this.stats]
        this.data.columns = ['Positive Score']
        // render by updating the this.table model
        this.table = this.data
        this.running = false

        // compare the result to the threshold
        if (parseFloat(this.stats['Positive Score'])> 0.02) {
          console.log('MYOD1+')
        } else {
          console.log('MYOD1-')
        }

      }

      // clear the webpage if the job has failed
      if (this.job.status === 4) {
        this.running = false;
      }


      // now fetch the cohort that we need to compare against from girder storage.  This way the cohort
      // can be updated by changing the girder contents instead of hard-coding the web app.

      // create a spot in Girder for the output of the REST call to be placed
      const cohortItem = (await this.girderRest.post(
        `item?folderId=${this.scratchFolder._id}&name=cohort`,
      )).data

      // build the params to be passed into the REST call
      var params = optionsToParameters({
        cohortName: 'myod1',
        outnameId: cohortItem._id,
      });
      console.log('params:',params)
      // start the job by passing parameters to the REST call
      this.job = (await this.girderRest.post(
        `arbor_nova/cohort?${params}`,
      )).data;

      // wait for the job to finish
      await pollUntilJobComplete(this.girderRest, this.job, job => this.job = job);
      this.cohortData = csvParse((await this.girderRest.get(`item/${cohortItem._id}/download`)).data);
      console.log('returned cohort',this.cohortData)

      // render the image statistics below the image

      // build the spec here.  Inside the method means that the data item will be available.  This spec is a boxplot of the cohort
      // of data with a vertical line superimposed over the calculation for this particular image. 

      var vegaLiteSpec = {
          "title": "MYOD1 Mutation of Uploaded Image Compared to Our Cohort",
          "height":250,
          "width": 500,
          "data": {
            "values": this.cohortData },
          "layer": [
            {
              "mark": "boxplot",
              "encoding": {
                "x": {
                  "field": "Positive Score",
                  "type": "quantitative",
                  "scale": {"zero": true}
                },
                "y": {
                  "field": "Category",
                  "type": "nominal"
                },
                "size": {"value":40},
                "color": {
                  "field": "Category",
                  "type":"nominal",
                  "scale": {"domain":["MYOD1-","MYOD1+","Uploaded Image"],"range": ["blue","red","orange"]}
                }
                }
              }, 
              {
                  "mark": "rule",
                  "data": {
                    "values": [
                      {"Category": "Uploaded Image", "Positive Score": this.stats['Positive Score']}
                    ]
                  },
                  "encoding": {
                    "x": {
                      "field": "Positive Score",
                      "type": "quantitative"
                    },
                    "color": {"value": "orange"},
                    "size": {"value": 4}
                  }
                },
                {
                  "mark": {
                      "type":"text",
                      "fontSize": 14,
                      "dx": 65
                      },
                  "data": {
                    "values": [
                      {"Category": "Uploaded Image", "Positive Score": this.stats['Positive Score']}
                    ]
                  },
                  "encoding": {
                    "text": {"field":"Positive Score","type":"quantitative"},
                    "x": {
                      "field": "Positive Score",
                      "type": "quantitative"
                    },
                    "y": {
                        "field": "Category",
                        "type": "ordinal"
                        },
                    "color": {"value": "orange"}
                  }
                }
            ]
        };
      // render the chart with options to save as PNG or SVG, but other options turned off
      vegaEmbed(this.$refs.visModel,vegaLiteSpec,
                {padding: 10, actions: {export: true, source: false, editor: false, compiled: false}});

    },


    async uploadImageFile_original(file) {
      if (file) {
        this.runCompleted = false;
        this.imageFileName = file.name;
        const uploader = new utils.Upload(file, {$rest: this.girderRest, parent: this.scratchFolder});
        this.uploadInProgress = true;
        this.imageFile = await uploader.start();
        // display the uploaded image on the webpage
	      console.log('displaying input image...');
        //this.imageBlob = (await this.girderRest.get(`file/${this.imageFile._id}/download`,{responseType:'blob'})).data;
        //this.uploadedImageUrl = window.URL.createObjectURL(this.imageBlob);
	      //console.log('createObjURL returned: ',this.uploadedImageUrl);
        this.readyToDisplayInput = true;
        this.renderInputImage();
      }
    },

 
    // display the progress of the image upload operation; called by uploadImageFile method during the upload process
    async receiveUploadProgress(status) {
      //console.log(status.current,status.size)
      this.progressUpload = (status.current/status.size*100.0).toString()
      console.log('upload progress:',this.progressUpload)
    },

    // upload a file in multiple chunks to support large WSI files; a callback is supported to show progress
    async uploadImageFile(file) {
      if (file) {
        this.runCompleted = false;
        this.imageFileName = file.name;
        this.uploadInProgress = true;
        // this upload manager splits the file into smaller transfers to allow uploading a large file with a progress bar
        const uploader = new UploadManager(file, {$rest: this.girderRest, parent: this.scratchFolder,progress: this.receiveUploadProgress});
        this.imageFile = await uploader.start();
        // display the uploaded image on the webpage
	      console.log('displaying input image...');
        this.readyToDisplayInput = true;
        this.uploadInProgress = false;
        this.renderInputImage();
      }
    },


    // display the progress of the image upload operation; called by uploadImageFile method during the upload process
    async receiveSegmentationUploadProgress(status) {
      //console.log(status.current,status.size)
      this.segmentationProgressUpload = (status.current/status.size*100.0).toString()
      console.log('upload progress:',this.segmentationProgressUpload)
    },


    async uploadSegmentationFile(file) {
      if (file) {
        this.runCompleted = false;
        this.segmentFileName = file.name;
        const uploader = new UploadManager(file, {$rest: this.girderRest, parent: this.scratchFolder,progress: this.receiveSegmentationUploadProgress});
        this.segmentUploadInProgress = true;
        this.segmentFile = await uploader.start();
        // display the uploaded image on the webpage
        this.segmentUploadInProgress = false;
	      console.log('received segmentation image...');
        this.readyToDisplaySegmentation = true;
        this.renderSegmentImage();
      }
    },



    // display the progress of the image upload operation; called by uploadImageFile method during the upload process
    async updateSegmentationJobStatus(job) {
      this.job = job
      // pick out the last print message from the job

      var last_element = job.log[job.log.length - 1];
        if (last_element) {
        //console.log(last_element)
        let lastIndex = last_element.lastIndexOf('\n')
        //console.log('lastindex:',lastIndex)
        let progressSnippet = last_element.substring(lastIndex)
        //console.log(progressSnippet)
        //console.log(progressSnippet.substring(1,9))
        //console.log(progressSnippet.substring(1,2))
        // if this is a progress update string, then extract the percentage done and update the state variable
        if (progressSnippet.substring(1,9)=='progress') {
          // starting at this position, is the string of the value to update the progress bar
          this.progressSegmentation = progressSnippet.substring(11)
          //console.log('percentage:',this.progressSegmentation)
        }
      }
    },


    // this routine is called when the user indicates they want to run the analysis, but there is no
    // segmentation file specifically loaded.  In this case, run the segmentation model and upload the result
    // to the UI

    async generateSegmentation() {
        this.runCompleted = false;
        this.segmentUploadInProgress = true;
        this.segmentFileName = 'Generating Segmentation...'

        // create a spot in Girder for the output of the REST call to be placed
        const outputItem = (await this.girderRest.post(
          `item?folderId=${this.scratchFolder._id}&name=segmentResult`,
        )).data

        // create a spot in Girder for the output of the REST call to be placed
        const statsItem = (await this.girderRest.post(
          `item?folderId=${this.scratchFolder._id}&name=stats`,
        )).data

        // build the params to be passed into the REST call
        const params = optionsToParameters({
          imageId: this.imageFile._id,
          outputId: outputItem._id,
          statsId: statsItem._id
        });
        // start the job by passing parameters to the REST call
        this.job = (await this.girderRest.post(
          `arbor_nova/infer_rms_map?${params}`,
        )).data;

        // wait for the job to finish
        await pollUntilJobComplete(this.girderRest, this.job, this.updateSegmentationJobStatus);


        // display the uploaded image on the webpage
        this.segmentUploadInProgress = false;
	      console.log('calculated segmentation image...');
        this.segmentResult = (await this.girderRest.get(`item/${outputItem._id}/download`,{responseType:'blob'})).data;
        this.segmentFileName = 'Generated Segmentation'

         // set this variable to display the resulting output image on the webpage 
        this.readyToDisplaySegmentation = true;
        this.segmentImageUrl = window.URL.createObjectURL(this.segmentResult);

        console.log('generate segment finished')

        // ACTION - get the item's file 
        //  lookup right here 
        this.segmentFile = (await this.girderRest.get(`item/${outputItem._id}/files`)).data[0];
        this.renderSegmentImage()

        return this.segmentImageUrl
    },


    // loading a sample image means loading the WSI and a corresponding segmentation.  Both of these are done
    // here.  This requires girder to be pre-loaded with image names that match the patterns here. 

    async loadSampleImageFile() {
          console.log('load sample image')
          this.runCompleted = false;
          this.uploadInProgress = true;
          this.imageFileName = 'Sample_WSI_Image.svs'
          const params = optionsToParameters({
                q: this.imageFileName,
                types: JSON.stringify(["file"])
              });
          // find the sample image already uploaded in Girder
          this.fileId = (await this.girderRest.get(
            `resource/search?${params}`,
          )).data["file"][0];

          console.log('displaying sample input stored at girder ID:',this.fileId);
          this.imageFile = this.fileId
          this.uploadInProgress = false;
          this.inputDisplayed == false;
          this.renderInputImage();

          // now get the segmentation image to match the WSI
          this.segmentUploadInProgress = true
          this.segmentFileName = 'Sample_WSI_Segmentation.png'
          const params2 = optionsToParameters({
                q: this.segmentFileName,
                types: JSON.stringify(["file"])
              });
          // find the sample image already uploaded in Girder
          this.fileId = (await this.girderRest.get(
            `resource/search?${params2}`,
          )).data["file"][0];

          console.log('displaying sample segmentation stored at girder ID:',this.fileId);
          this.segmentFile = this.fileId
          this.segmentDisplayed = false;
          this.readyToDisplayInput = true;
          this.segmentUploadInProgress = false
          this.renderSegmentImage();
          this.running = false;
          },



    // download the segmentation image result when requested by the user
    async downloadResults() {
        console.log('download this:',this.result)
        const url = window.URL.createObjectURL(JSON.stringify(this.result));
	      console.log("url:",url)
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'infer_results.json') 
        document.body.appendChild(link);
        link.click();
	      document.body.removeChild(link);
    },

    // reload the page to allow the user to process another image.
    // this clears all state and image displays. The scroll command
    // resets the browser to the top of the page. 
    reset() {
      window.location.reload(true);
      window.scrollTo(0,0);
    },
  }
}
</script>
