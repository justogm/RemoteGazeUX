/**
 * Gaze Tracking Module
 *
 * This module handles all gaze tracking functionality using WebGazer.js
 * including calibration, point collection, and data management.
 */

export class GazeTracker {
  constructor() {
    // Calibration state
    this.pointCalibrate = 0;
    this.calibrationPoints = {};
    this.calibrated = false;
    this.accuracy = null; // Store accuracy measurement

    // Data collection
    this.points = [];
    this.mousePosition = { x: 0, y: 0 };

    // Configuration
    this.batchSize = 20; // Number of points to collect before sending

    // Callbacks
    this.onCalibrationComplete = null;
    this.onPointsBatchReady = null;
    this.onAccuracyCalculated = null;
  }

  /**
   * Updated initializeCanvas to align with demo setup logic.
   */
  initializeCanvas() {
    let canvas = document.getElementById("plotting_canvas");
    if (!canvas) {
      console.warn(
        "plotting_canvas not found during initialization. Creating a new one.",
      );
      canvas = document.createElement("canvas");
      canvas.id = "plotting_canvas";
      document.body.appendChild(canvas);
    }

    // Set up the canvas properties
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.position = "fixed";
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
        throw new Error(
          "No se pudo iniciar el stream de la cámara. Por favor, verifica que la cámara esté conectada y que hayas dado los permisos necesarios.",
        );
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
        const videoElement = document.querySelector("#webgazerVideoFeed");

        if (videoElement) {
          // Check if video has a valid stream
          if (videoElement.srcObject && videoElement.srcObject.active) {
            const videoTracks = videoElement.srcObject.getVideoTracks();
            if (
              videoTracks.length > 0 &&
              videoTracks[0].readyState === "live"
            ) {
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
      const isTaskBarVisible = taskBar && window.getComputedStyle(taskBar).display !== "none";

      if (this.calibrated && (!isTaskBarVisible)) {
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
        "#webgazerVideoContainer, #webgazerVideoFeed, video",
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
      "#webgazerVideoContainer, #webgazerVideoFeed, video",
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

      document.getElementById("Pt5").style.removeProperty("display");

      this.calcAccuracy();

      // Hide video immediately after calibration
      this.hideWebgazerVideo();

      // Trigger callback
      if (this.onCalibrationComplete) {
        this.onCalibrationComplete();
      }
    }
  }

  /**
   * Calculate the precision of gaze predictions based on the last 50 stored points
   */
  calcAccuracy() {
    // Ensure canvas is ready before starting to store points
    this.ensureCanvasReady();

    // Replace swal with Swal.fire for SweetAlert2 compatibility
    Swal.fire({
      title: "Calculating measurement",
      text: "Please don't move your mouse & stare at the middle dot for the next 5 seconds. This will allow us to calculate the accuracy of our predictions.",
      allowEscapeKey: false,
      allowOutsideClick: false,
      showCloseButton: true,
    }).then(() => {
      // makes the variables true for 5 seconds & plots the points

      store_points_variable(); // start storing the prediction points

      sleep(5000).then(() => {
        stop_storing_points_variable(); // stop storing the prediction points
        var past50 = webgazer.getStoredPoints(); // retrieve the stored points
        // Debugging: Check if points are being stored
        // Debugging: Log retrieved points
        var precision_measurement = calculatePrecision(past50);

        // Store accuracy in the instance
        this.accuracy = precision_measurement;

        // Trigger accuracy calculation callback
        if (this.onAccuracyCalculated) {
          this.onAccuracyCalculated(precision_measurement);
        }

        if (precision_measurement >= 70) {
          Swal.fire({
            title: `Your accuracy measure is ${precision_measurement}%. Continue with the task!`,
            allowOutsideClick: false,
            icon: "success",
          }).then((result) => {
            if (result.isConfirmed) {
              // Handle confirm action for accuracy >= 70%
              this.clearCanvas();
              this.calibrated = true;
              console.log("Calibration confirmed. Proceeding with next steps.");

              document.querySelectorAll(".Calibration").forEach((i) => {
                i.style.setProperty("display", "none");
              });

              // Trigger callback
              if (this.onCalibrationComplete) {
                this.onCalibrationComplete();
              }
            }
          });
        } else {
          Swal.fire({
            title: `Your accuracy measure is ${precision_measurement}%. Recalibration is needed.`,
            allowOutsideClick: false,
            icon: "error",
          }).then((result) => {
            if (result.isConfirmed) {
              // Handle confirm action for accuracy < 70%
              console.log(
                "Recalibration requested. Restarting calibration process.",
              );
              this.restart();
            }
          });
        }
      });
    });
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
   * Enhanced clearCanvas to ensure plotting_canvas is always created.
   */
  clearCanvas() {
    let canvas = document.getElementById("plotting_canvas");
    if (!canvas) {
      console.warn("plotting_canvas not found. Creating a new one.");
      canvas = document.createElement("canvas");
      canvas.id = "plotting_canvas";
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      document.body.appendChild(canvas);
    } else {
      canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  /**
   * Ensure canvas is ready for drawing gaze points
   * This must be called before webgazer.params.storingPoints is set to true
   */
  ensureCanvasReady() {
    let canvas = document.getElementById("plotting_canvas");
    if (!canvas) {
      console.warn("plotting_canvas not found. Creating it now.");
      canvas = document.createElement("canvas");
      canvas.id = "plotting_canvas";
      canvas.style.position = "fixed";
      canvas.style.top = "0";
      canvas.style.left = "0";
      canvas.style.zIndex = "999";
      canvas.style.display = "block";
      document.body.appendChild(canvas);
    }

    // Ensure canvas has proper dimensions and can be accessed
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
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
    if (typeof webgazer !== "undefined") {
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

  /**
   * Set callback for when accuracy is calculated
   */
  setOnAccuracyCalculated(callback) {
    this.onAccuracyCalculated = callback;
  }
}

// Export for use in other modules
window.GazeTracker = GazeTracker;

// Import store_points_variable and stop_storing_points_variable from precision_calculation.js
// Ensure these functions are accessible
import {
  store_points_variable,
  stop_storing_points_variable,
} from "./precision_calculation.js";

// Import calculatePrecision from precision_calculation.js
import { calculatePrecision } from "./precision_calculation.js";

// Utility function to pause execution for a given duration
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
