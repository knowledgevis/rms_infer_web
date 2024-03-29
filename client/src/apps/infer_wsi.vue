<template>
  <v-app>
    <v-layout class="transform-view" row fill-height>
      <v-navigation-drawer permanent fixed style="width: 400px; min-width: 400px;">
        <v-toolbar dark flat color="primary">
          <v-toolbar-title class="white--text">Whole Slide RMS Segmentation</v-toolbar-title>
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
          <v-flex xs12>
            <v-btn
              block
              :class="{ primary: readyToRun }"
              :flat="readyToRun"
              :outline="!readyToRun"
              :disabled="!readyToRun"
              @click="run"
            >
              Segment the Image
            </v-btn>
          </v-flex>
          <v-flex xs12>
            <v-btn
              block
              :class="{ primary: readyToDownload }"
              :flat="readyToDownload"
              :outline="!readyToDownload"
              :disabled="!readyToDownload"
              @click="downloadResults"
            >
              Download Segmentation Image 
            </v-btn>
          </v-flex>
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
              <b>This application segments a whole slide image by executing a neural network that has
              been pre-trained to segment rhabdomyosarcoma tissue subtypes in H&E stained   
              whole slide images.  Uploaded images can be in Aperio (.svs) format or they can be pyramidal TIF files.  This algorithm 
              has been validated using 10x magnification images.  Other uploaded image magnifications will be resampled to 10x before 
              being analyzed. 
              <br><br>
              Please attempt this application on a computer system with at least 32GB of memory (as the absolute minumum).  We encourage the use of a recent NVIDIA GPU
              with at least 12GB of GPU memory and at least 128GB of system memory to process larger images. In our experience, insuffient system memory is the most likely cause if 
              this application does not finish successfully.  If you are using Docker Desktop application to run this image, it is likely you will need to go into the Resources 
                tab and increase the "Memory Size" to be as large as possible for your particular system (at least 32GB). 
              <br><br>
              After selecting an image for upload, be patient during the upload process. Once the input image is displayed below, please click the "Segment the Image" button to begin execution.  Execution may take up to several minutes,
              depending on the size of the input image being provided.  When the analysis is complete, the resulting segmentation
              will be displayed below and will be available for downloading, using the download button.  
              <br><br>
              If the progress bar stops further advancing for a few
              minutes, please refresh the browser page and try again with a smaller image. Failures happen most often when the application runs out of available system memory.  
              <br><br>
              If you would like to segment additional images, please just click "Prepare for Another Image" in between each segmentation operation. This tells the system to reset and prepare to run again.  
              <br><br>
              We are delighted that you are trying our early release system for rhabdomyosarcoma analysis. Thank you.  
              </b>
            </v-card-text>
            
          </v-card>
           <div v-if="uploadIsHappening" xs12 class="text-xs-center mb-4 ml-4 mr-4">
           Image Upload in process...
           <v-progress-linear :value="progressUpload"></v-progress-linear>
          </div>

          <div v-if="thumbnailInProgress" xs12 class="text-xs-center mb-4 ml-4 mr-4">
            Generating a thumbnail of the uploaded image
            <v-progress-linear indeterminate=True></v-progress-linear>
          </div>

        <div  xs12 class="text-xs-center mb-4 ml-4 mr-4">
  	       <v-card v-if="inputReadyForDisplay" class="mb-4 ml-4 mr-4">
            <v-card-text>Uploaded Image</v-card-text>
               <img :src="inputImageUrl" style="display: block; margin: auto"> 
            </v-card>
        </div>

        <v-card v-if="running && job.status==0" xs12 class="text-xs-center mb-4 ml-4 mr-4">
            Another user is currently using the system.  Please wait.  Your inferencing job should begin automatically when the previous job completes. 
            <v-progress-linear indeterminate=True></v-progress-linear>
        </v-card>
        <v-card v-if="running && job.status == 2" xs12 class="text-xs-center mb-4 ml-4 mr-4">
            Running the Segmentation Neural Network.  Please wait for the output image to show below. 
            This will take several minutes.  
          <v-progress-linear :value="progress"></v-progress-linear>
        </v-card>

        <div v-if="runCompleted" xs12 class="text-xs-center mb-4 ml-4 mr-4">
          Job Complete  ... 
        </div>
        <code v-if="!running && job.status === 4" class="mb-4 ml-4 mr-4" style="width: 100%">{{ job.log.join('\n') }}</code> 

        <div v-show="runCompleted && job.status == 3">
  	     <v-card class="mb-4 ml-4 mr-4">
            <v-card-text>Segmentation Image</v-card-text>
		          {{ renderOutputImage(outputImageUrl) }} 
          </v-card>

          <v-card class="mb-4 ml-4 mr-4">  
           <div ref="outputImageDiv" id ="openseadragon2" style="width:1000px;height:800px; margin: auto;"> </div>
          </v-card>

          <v-card  align="center" justify="center" class="mt-20 mb-4 ml-4 mr-4">

            <v-card-text>
              <b>Below is a chart showing the percentages of ARMS, ERMS, Stroma, and Necrosis in the WSI as predicted
            by our segmentation algorithm.  Click the elipsis icon at the top right to save a copy of the chart
            to your local system
              </b>
              <br>
            </v-card-text>

             <div id="visM" ref="visModel" class="mt-20 mb-4 ml-4 mr-4"></div>
          </v-card>

          <v-card v-if="table.length > 0" class="mt-8 mb-4 ml-4 mr-4">
            <v-card-text>Image Statistics</v-card-text>
            <json-data-table :data="table" />
          </v-card>
        </div>



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
import OpenSeadragon from 'openseadragon';
import vegaEmbed from 'vega-embed';
import UploadManager from '../utils/upload';


export default {
  name: 'infer_rhabdo',
  inject: ['girderRest'],
  components: {
    JsonDataTable,
  },
  data: () => ({
    imageFile: {},
    imageFileName: '',
    imagePointer: '',
    imageBlob: [],
    uploadedImageUrl: '',
    job: { status: 0 },
    readyToDisplayInput: false,
    running: false,
    thumbnail: [],
    result: [],
    table: [],
    stats: [],
    data: [],
    resultColumns: [],
    resultString:  '',
    runCompleted: false,
    uploadInProgress: false,
    thumbnailInProgress: false,
    inputImageUrl: '',
    outputImageUrl: '',
    inputDisplayed:  false,
    outputDisplayed:  false,
    osd_viewer: [],
    imageStats: {},
    progress: "0",
    progressUpload: "0",
  }),
  asyncComputed: {
    scratchFolder() {
      return scratchFolder(this.girderRest);
    },
  },
  computed: {
    readyToRun() {
      return !!this.imageFileName; 
    },
    readyToDownload() {
      return (this.runCompleted)
    },
    uploadIsHappening() {
      return (this.uploadInProgress)
    },
    inputReadyForDisplay() {
      return this.inputDisplayed
    }
  },

  methods: {

    // method here to create and display a thumbnail of an arbitrarily large whole slilde image.
    // This code is re-executed for each UI change, so the code is gated to only run once.  We only clear the "upload in progress"
    // after the thumbnail calculation is finished so the user doesn't wonder what is happening during thumbnail calculation. 

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
          }

          console.log('render input finished')
          this.inputDisplayed = true
          this.thumbnailInProgress = false
	     }
    },



    // method is added here to enable openSeadragon to render the output image into a div defined in the vue template
    // above.  This code is re-executed for each change, so the code is gated to only run once 
    renderOutputImage(imageurl) {
       if ((this.outputDisplayed == false) & (this.outputImageUrl.length > 0)) {
        console.log('output url:',imageurl)
      var viewer2 =  OpenSeadragon( {
	       element: this.$refs.outputImageDiv, 
	       maxZoomPixelRatio: 4.0,
         prefixUrl: "/static/arbornova/images/",
         tileSources: {
          type: 'image',
          url:   imageurl
    	  }
      	});
        console.log('openseadragon output finished')
      	this.outputDisplayed = true
      	}
      },

    updateJobStatus(job) {
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
          this.progress = progressSnippet.substring(11)
          console.log('percentage:',this.progress)
        }
      }
    },

    async run() {
      this.running = true;
      this.errorLog = null;

      // create a spot in Girder for the output of the REST call to be placed
      const outputItem = (await this.girderRest.post(
        `item?folderId=${this.scratchFolder._id}&name=result`,
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
        `arbor_nova/infer_wsi?${params}`,
      )).data;

      // wait for the job to finish
      await pollUntilJobComplete(this.girderRest, this.job, this.updateJobStatus);

      if (this.job.status === 3) {
        this.running = false;
	       // pull the URL of the output from girder when processing is completed. This is used
	       // as input to an image on the web interface
        this.result = (await this.girderRest.get(`item/${outputItem._id}/download`,{responseType:'blob'})).data;
	       // set this variable to display the resulting output image on the webpage 
        this.outputImageUrl = window.URL.createObjectURL(this.result);

        // get the stats returned
        this.stats = (await this.girderRest.get(`item/${statsItem._id}/download`,{responseType:'text'})).data;
        console.log('returned stats',this.stats)
        console.log('parsed stats',this.stats.ARMS, this.stats.ERMS,this.stats.necrosis)

        // copy this data to a state variable for rendering in a table
        this.data = [this.stats]
        this.data.columns = ['ARMS','ERMS','necrosis','stroma']
        // render by updating the this.table model
        this.table = this.data

        // render the image statistics below the image
        this.runCompleted = true;

        // build the spec here.  Inside the method means that the data item will be available. 
        let titleString = 'Percentage of the slide positive for each tissue class'

      var vegaLiteSpec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
            "description": "A simple bar chart with embedded data.",
             title: titleString,
              "height": 450,
              "width": 600,
              "autosize": {
                "type": "fit",
                "contains": "padding"
              },
            "data": {
              "values": [
                {"Class": "ARMS","percent": this.stats.ARMS}, 
                {"Class": "ERMS","percent": this.stats.ERMS}, 
                {"Class": "Stroma","percent": this.stats.stroma}, 
                {"Class": "Necrosis","percent": this.stats.necrosis}
              ]
            },
           "layer": [{
              "mark": "bar"
            }, {
              "mark": {
                "type": "text",
                "align": "center",
                "baseline": "bottom",
                "fontSize": 13,
                "dx": 0,
              },
              "encoding": {
                "text": {"field": "percent", "type": "quantitative","color":{"value":"black"}}
              }
            }],
            "encoding": {
              "x": {"field": "Class", "type": "ordinal","title":"Tissue Classification"},
              "y": {"field": "percent", "type": "quantitative","title":"Percent of tissue positive for each class"},
              "color": {
                  "field": "Class",
                  "type":"nominal",
                  "scale": {"domain":["ARMS","ERMS","Necrosis","Stroma"],"range": ["blue","red","gold","lightgreen"]}
                  }
            }
          };
          // render the chart with options to save as PNG or SVG, but other options turned off
          vegaEmbed(this.$refs.visModel,vegaLiteSpec,
                 {padding: 10, actions: {export: true, source: false, editor: false, compiled: false}});
      }
      if (this.job.status === 4) {
        this.running = false;
      }
    },


    async uploadImageFile_non_chunked(file) {
      if (file) {
        this.runCompleted = false;
        this.imageFileName = file.name;
        this.uploadInProgress = true;
        const uploader = new utils.Upload(file, {$rest: this.girderRest, parent: this.scratchFolder});
        this.imageFile = await uploader.start();
        // display the uploaded image on the webpage
	      console.log('displaying input image...');
        //this.imageBlob = (await this.girderRest.get(`file/${this.imageFile._id}/download`,{responseType:'blob'})).data;
        //this.uploadedImageUrl = window.URL.createObjectURL(this.imageBlob);
	      //console.log('createObjURL returned: ',this.uploadedImageUrl);
        this.readyToDisplayInput = true;
        this.uploadInProgress = false;
        this.renderInputImage();
      }
    },

    // display the progress of the image upload operation; called by uploadImageFile method during the upload process
    async receiveProgress(status) {
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
        const uploader = new UploadManager(file, {$rest: this.girderRest, parent: this.scratchFolder,progress: this.receiveProgress});
        this.imageFile = await uploader.start();
        // display the uploaded image on the webpage
	      console.log('displaying input image...');
        //this.imageBlob = (await this.girderRest.get(`file/${this.imageFile._id}/download`,{responseType:'blob'})).data;
        //this.uploadedImageUrl = window.URL.createObjectURL(this.imageBlob);
	      //console.log('createObjURL returned: ',this.uploadedImageUrl);
        this.readyToDisplayInput = true;
        this.uploadInProgress = false;
        this.renderInputImage();
      }
    },



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
        this.readyToDisplayInput = true;
        this.renderInputImage();
        },



    // download the segmentation image result when requested by the user
    async downloadResults() {
        const url = window.URL.createObjectURL(this.result);
	      console.log("url:",url)
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'infer_results.png') 
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
