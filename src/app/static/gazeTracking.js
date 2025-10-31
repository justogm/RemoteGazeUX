/**
 * Gaze Tracking Module
 * 
 * This module handles all gaze tracking functionality using WebGazer.js
 * including calibration, point collection, and data management.
 */

class GazeTracker {
  constructor() {
    // Calibration state
    this.pointCalibrate = 0;
    this.calibrationPoints = {};
    this.calibrated = false;

    // Data collection
    this.points = [];
    this.mousePosition = { x: 0, y: 0 };

    // Configuration
    this.batchSize = 20; // Number of points to collect before sending

    // Callbacks
    this.onCalibrationComplete = null;
    this.onPointsBatchReady = null;
  }

  /**
   * Initialize WebGazer and set up tracking
   */
  async initialize() {
    try {
      // Start the webgazer tracker
      await webgazer
        .setRegression("ridge")
        .setTracker("TFFacemesh")
        .saveDataAcrossSessions(true)
        .begin();

      // Verify that the video stream is available
      const isVideoStreamReady = await this.checkVideoStream();
      if (!isVideoStreamReady) {
        throw new Error("No se pudo iniciar el stream de la cámara. Por favor, verifica que la cámara esté conectada y que hayas dado los permisos necesarios.");
      }

      // Configure webgazer
      webgazer
        .showVideoPreview(false)
        .showPredictionPoints(false)
        .applyKalmanFilter(true);

      // Hide video after initialization
      setTimeout(() => {
        this.hideWebgazerVideo();
      }, 1000);

      // Set up gaze listener
      this.setupGazeListener();

      // Set up mouse tracking
      this.setupMouseTracking();

      // Set up video observer
      this.setupVideoObserver();

      console.log("GazeTracker initialized successfully");
    } catch (error) {
      console.error("Error initializing GazeTracker:", error);
      throw error;
    }
  }

  /**
   * Check if the video stream is ready and working
   * @returns {Promise<boolean>} True if video stream is available
   */
  async checkVideoStream() {
    return new Promise((resolve) => {
      let attempts = 0;
      const maxAttempts = 30; // 3 seconds (30 * 100ms)
      
      const checkInterval = setInterval(() => {
        attempts++;
        
        // Try to find the video element
        const videoElement = document.querySelector('#webgazerVideoFeed');
        
        if (videoElement) {
          // Check if video has a valid stream
          if (videoElement.srcObject && videoElement.srcObject.active) {
            const videoTracks = videoElement.srcObject.getVideoTracks();
            if (videoTracks.length > 0 && videoTracks[0].readyState === 'live') {
              console.log("Video stream is ready and active");
              clearInterval(checkInterval);
              resolve(true);
              return;
            }
          }
        }
        
        // If max attempts reached, assume failure
        if (attempts >= maxAttempts) {
          console.error("Video stream not detected after maximum attempts");
          clearInterval(checkInterval);
          resolve(false);
        }
      }, 100);
    });
  }

  /**
   * Set up the gaze listener to collect points
   */
  setupGazeListener() {
    webgazer.setGazeListener((data, elapsedTime) => {
      if (data == null) {
        return;
      }
      webgazer.util.bound(data);

      const taskBar = document.getElementById("task-bar");

      if (this.calibrated && taskBar && taskBar.style.display !== "block") {
        const xprediction = data.x;
        const yprediction = data.y;

        // Add the current timestamp to each point
        const currentTimestamp = new Date().toLocaleString("en-US", {
          timeZone: "America/Argentina/Buenos_Aires",
        });

        this.points.push({
          date: currentTimestamp,
          gaze: {
            x: xprediction,
            y: yprediction,
          },
          mouse: {
            x: this.mousePosition.x,
            y: this.mousePosition.y,
          },
        });

        // Send points in batches
        if (this.points.length >= this.batchSize) {
          console.log("Batch ready, sending points...");
          console.log(this.points);
          
          if (this.onPointsBatchReady) {
            this.onPointsBatchReady([...this.points]);
          }
          
          this.points = [];
        }
      }
    });
  }

  /**
   * Set up mouse position tracking
   */
  setupMouseTracking() {
    document.addEventListener("mousemove", (event) => {
      if (this.calibrated) {
        this.mousePosition.x = event.clientX;
        this.mousePosition.y = event.clientY;
      }
    });
  }

  /**
   * Set up mutation observer to hide video elements
   */
  setupVideoObserver() {
    const observer = new MutationObserver(() => {
      const videos = document.querySelectorAll(
        "#webgazerVideoContainer, #webgazerVideoFeed, video"
      );
      videos.forEach((video) => {
        if (this.calibrated) {
          video.style.display = "none";
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  /**
   * Hide the webgazer video preview
   */
  hideWebgazerVideo() {
    webgazer.showVideoPreview(false);

    const videos = document.querySelectorAll(
      "#webgazerVideoContainer, #webgazerVideoFeed, video"
    );
    videos.forEach((video) => {
      video.style.display = "none";
    });
  }

  /**
   * Show calibration points on the page
   */
  showCalibrationPoints() {
    document.querySelectorAll(".Calibration").forEach((i) => {
      i.style.removeProperty("display");
    });
    // Initially hide the middle button
    const pt5 = document.getElementById("Pt5");
    if (pt5) {
      pt5.style.setProperty("display", "none");
    }
  }

  /**
   * Set up calibration point click handlers
   */
  setupCalibration() {
    document.querySelectorAll(".Calibration").forEach((element) => {
      element.addEventListener("click", () => {
        this.handleCalibrationClick(element);
      });
    });

    this.showCalibrationPoints();
  }

  /**
   * Handle calibration point click
   */
  handleCalibrationClick(node) {
    const id = node.id;

    if (!this.calibrationPoints[id]) {
      this.calibrationPoints[id] = 0;
    }
    this.calibrationPoints[id]++;

    if (this.calibrationPoints[id] === 5) {
      // Turn to yellow after 5 clicks
      node.style.setProperty("background-color", "yellow");
      node.setAttribute("disabled", "disabled");
      this.pointCalibrate++;
    } else if (this.calibrationPoints[id] < 5) {
      // Gradually increase opacity
      const opacity = 0.2 * this.calibrationPoints[id] + 0.2;
      node.style.setProperty("opacity", opacity);
    }

    // Show middle calibration point after all other points
    if (this.pointCalibrate === 8) {
      const pt5 = document.getElementById("Pt5");
      if (pt5) {
        pt5.style.removeProperty("display");
      }
    }

    if (this.pointCalibrate >= 9) {
      // Last point is calibrated
      document.querySelectorAll(".Calibration").forEach((i) => {
        i.style.setProperty("display", "none");
      });

      this.calibrated = true;

      // Hide video immediately after calibration
      this.hideWebgazerVideo();

      // Trigger callback
      if (this.onCalibrationComplete) {
        this.onCalibrationComplete();
      }
    }
  }

  /**
   * Restart the calibration process
   */
  restart() {
    webgazer.clearData();
    this.clearCalibration();
    this.pointCalibrate = 0;
    this.calibrationPoints = {};
    this.calibrated = false;
  }

  /**
   * Clear calibration data
   */
  clearCalibration() {
    this.calibrationPoints = {};
    this.pointCalibrate = 0;
    this.calibrated = false;
    
    // Reset calibration points UI
    document.querySelectorAll(".Calibration").forEach((i) => {
      i.style.removeProperty("background-color");
      i.removeAttribute("disabled");
      i.style.setProperty("opacity", "0.2");
    });

    this.showCalibrationPoints();
  }

  /**
   * Enable point storage
   */
  storePoints() {
    if (typeof webgazer !== 'undefined' && webgazer.params) {
      webgazer.params.storingPoints = true;
    }
  }

  /**
   * Disable point storage
   */
  stopStoringPoints() {
    if (typeof webgazer !== 'undefined' && webgazer.params) {
      webgazer.params.storingPoints = false;
    }
  }

  /**
   * Check if calibration is complete
   */
  isCalibrated() {
    return this.calibrated;
  }

  /**
   * Clean up and end tracking
   */
  end() {
    if (typeof webgazer !== 'undefined') {
      webgazer.end();
    }
  }

  /**
   * Set callback for when calibration is complete
   */
  setOnCalibrationComplete(callback) {
    this.onCalibrationComplete = callback;
  }

  /**
   * Set callback for when a batch of points is ready
   */
  setOnPointsBatchReady(callback) {
    this.onPointsBatchReady = callback;
  }
}

// Export for use in other modules
window.GazeTracker = GazeTracker;
