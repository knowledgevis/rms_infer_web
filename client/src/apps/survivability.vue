<template>
  <v-app>
    <v-layout class="transform-view" row fill-height>
      <v-navigation-drawer permanent fixed style="width: 400px; min-width: 400px;">
        <v-toolbar dark flat color="primary">
          <v-toolbar-title class="white--text">RMS Survivability Classification</v-toolbar-title>
          </v-toolbar>
          <v-spacer/>
          <v-container fluid>

          <v-flex xs12>
            <v-btn class="text-none" outline block @click='$refs.imageFile.click()'>{{ fastaFileName || 'UPLOAD Whole Slide Image' }}</v-btn>
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
              Go
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
              Download Results 
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
              <b>
		An ensemble model, constructed by combining a set of neural network models, has been trained to generate a risk prediction from an H&E whole slide.
    This application runs the model on an uploaded image to generate risk categories derived from our research cohort. 
		Uploaded images can be in Aperio (.svs) format or they can be pyramidal TIF files.
              <br><br>
		After selecting an image for upload, please be patient during the upload process. Once the input image is displayed below, please click the "Go" button to begin execution.  Execution may take up to several minutes,
		depending on the size of the input image being provided.  When the analysis is complete, the analysis result
		will be displayed below and will be available for downloading, using the download button.  If you would like to segment additional images, please just click "Prepare for Another Image" in between each segmentation operation. This tells the system to reset and prepare to run again.  
              <br><br>
		We are delighted that you are trying our early release system for rhabdomyosarcoma analysis. Thank you.  
		If you have any questions while using our system, please feel free to email Dr. Yanling Liu at liuy5@mail.nih.gov.  
		</b>
            </v-card-text>
          </v-card>
           <div v-if="uploadIsHappening" xs12 class="text-xs-center mb-4 ml-4 mr-4">
           Image Upload in process...
           <v-progress-linear indeterminate=True></v-progress-linear>
        </div>
        <div  xs12 class="text-xs-center mb-4 ml-4 mr-4">
  	       <v-card class="mb-4 ml-4 mr-4">
            <v-card-text>Uploaded Image</v-card-text>
               <img :src="inputImageUrl" style="display: block; margin: auto"> 
            </v-card>
        </div>

        <div v-if="running" xs12 class="text-xs-center mb-4 ml-4 mr-4">
          Running (Job Status {{ job.status }}) ... please wait for the output image to show below
          <v-progress-linear indeterminate=True></v-progress-linear>
        </div>
        <div v-if="runCompleted" xs12 class="text-xs-center mb-4 ml-4 mr-4">
          Job Complete  ... 
        </div>
        <code v-if="!running && job.status === 4" class="mb-4 ml-4 mr-4" style="width: 100%">{{ job.log.join('\n') }}</code> 
        <div v-if="!running && job.status === 3">
  	  <v-card class="mb-4 ml-4 mr-4">
            <v-card-text>Segmentation Image</v-card-text>
		          {{ renderOutputImage(outputImageUrl) }} 
          </v-card>
        </div>
    	<div ref="outputImageDiv" id ="openseadragon2" style="width:1000px;height:800px; margin: auto;"> </div>
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

export default {
  name: 'survivability',
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
    resultColumns: [],
    resultString:  '',
    runCompleted: false,
    uploadInProgress: false,
    inputImageUrl: '',
    outputImageUrl: '',
    inputDisplayed:  false,
    outputDisplayed:  false,
    osd_viewer: [],
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
  },

  methods: {

    // method here to create and display a thumbnail of an arbitrarily large whole slilde image.
    // This code is re-executed for each UI change, so the code is gated to only run once 

    async renderInputImage() {
       if (this.inputDisplayed == false) {

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

    async run() {
      this.running = true;
      this.errorLog = null;

      // create a spot in Girder for the output of the REST call to be placed
      const outputItem = (await this.girderRest.post(
        `item?folderId=${this.scratchFolder._id}&name=result`,
      )).data

      // build the params to be passed into the REST call
      const params = optionsToParameters({
        imageId: this.imageFile._id,
        outputId: outputItem._id,
      });
      // start the job by passing parameters to the REST call
      this.job = (await this.girderRest.post(
        `arbor_nova/infer_wsi?${params}`,
      )).data;

      // wait for the job to finish
      await pollUntilJobComplete(this.girderRest, this.job, job => this.job = job);

      if (this.job.status === 3) {
        this.running = false;
	// pull the URL of the output from girder when processing is completed. This is used
	// as input to an image on the web interface
        this.result = (await this.girderRest.get(`item/${outputItem._id}/download`,{responseType:'blob'})).data;
	// set this variable to display the resulting output image on the webpage 
        this.outputImageUrl = window.URL.createObjectURL(this.result);
	this.runCompleted = true;
      }
      if (this.job.status === 4) {
        this.running = false;
      }
    },


    async uploadImageFile(file) {
      if (file) {
        this.runCompleted = false;
        this.imageFileName = file.name;
        const uploader = new utils.Upload(file, {$rest: this.girderRest, parent: this.scratchFolder});
        this.uploadInProgress = true;
        this.imageFile = await uploader.start();
        // display the uploaded image on the webpage
        this.uploadInProgress = false;
	      console.log('displaying input image...');
        //this.imageBlob = (await this.girderRest.get(`file/${this.imageFile._id}/download`,{responseType:'blob'})).data;
        //this.uploadedImageUrl = window.URL.createObjectURL(this.imageBlob);
	      //console.log('createObjURL returned: ',this.uploadedImageUrl);
        this.readyToDisplayInput = true;
        this.renderInputImage();
      }
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