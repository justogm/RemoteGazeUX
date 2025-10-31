// Initialize gaze tracker instance
let gazeTracker = null;

function showPrototype() {
  document.getElementById("figma-prototype").style.display = "block";
}

document.addEventListener("DOMContentLoaded", function () {
  var myModal = new bootstrap.Modal(document.getElementById("modal-ayuda"));
  myModal.show();

  // Initialize gaze tracker
  gazeTracker = new GazeTracker();

  // Set up calibration
  gazeTracker.setupCalibration();

  // Set up calibration complete callback
  gazeTracker.setOnCalibrationComplete(() => {
    checkCalibrationAndShowButton();
  });

  // Set up points batch ready callback
  gazeTracker.setOnPointsBatchReady((points) => {
    enviarPuntos(points);
  });

  // Manejar el clic en el botón "Entendido"
  document
    .getElementById("btn-entendido")
    .addEventListener("click", function () {
      myModal.hide(); // Cierra el modal
    });
});

// -----------------------------
window.onload = async function () {
  // Initialize the gaze tracker
  if (gazeTracker) {
    try {
      await gazeTracker.initialize();
    } catch (error) {
      // Show error message to the user
      const errorMessage = document.createElement('div');
      errorMessage.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
        border-radius: 8px;
        padding: 30px;
        max-width: 500px;
        text-align: center;
        z-index: 10000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
      `;
      errorMessage.innerHTML = `
        <h3 style="margin-top: 0;">⚠️ Error de Cámara</h3>
        <p style="margin-bottom: 20px;">
          ${error.message || 'No se pudo acceder a la cámara. Por favor, verifica que esté conectada y que hayas dado los permisos necesarios.'}
        </p>
        <p style="font-size: 0.9em; margin-bottom: 20px;">
          Para continuar con el estudio, necesitas:
        </p>
        <ul style="text-align: left; margin-bottom: 20px;">
          <li>Permitir el acceso a la cámara en tu navegador</li>
          <li>Verificar que la cámara esté conectada y funcionando</li>
          <li>Intentar con otro navegador si el problema persiste</li>
        </ul>
        <button id="reload-btn" style="
          background-color: #721c24;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 5px;
          cursor: pointer;
          font-size: 16px;
        ">Recargar Página</button>
      `;
      
      document.body.appendChild(errorMessage);
      
      // Add reload functionality
      document.getElementById('reload-btn').addEventListener('click', () => {
        window.location.reload();
      });
      
      // Hide calibration points and prevent interaction
      document.querySelectorAll('.Calibration').forEach((element) => {
        element.style.display = 'none';
      });
      
      console.error('Camera initialization failed:', error);
    }
  }
};

// Set to true if you want to save the data even if you reload the page.
window.saveDataAcrossSessions = true;

window.onbeforeunload = function () {
  if (gazeTracker) {
    gazeTracker.end();
  }
};

/**
 * Restart the calibration process by clearing the local storage and reseting the calibration point
 */
function Restart() {
  if (gazeTracker) {
    gazeTracker.restart();
  }
}

function isCalibrated() {
  return gazeTracker ? gazeTracker.isCalibrated() : false;
}

/**
 * Saving data
 */
const urlParams = new URLSearchParams(window.location.search);
const id = urlParams.get("id");

document.addEventListener("DOMContentLoaded", function () {
  // Obtener la configuración desde la ruta /api/config
  fetch("/api/config")
    .then((response) => response.json())
    .then((config) => {
      const prototypeUrl = config.url_path;
      const imgPath = config.img_path;

      // Validar que uno de los dos esté configurado y no ambos
      if (
        (!prototypeUrl || prototypeUrl === "null") &&
        (!imgPath || imgPath === "null")
      ) {
        console.error(
          "Error: Ambos valores son nulos. Debe configurarse 'url_path' o 'img_path'."
        );
        alert(
          "Error: No se ha configurado correctamente el prototipo o la imagen."
        );
        return;
      }

      if (prototypeUrl && prototypeUrl !== "null") {
        // Mostrar el iframe del prototipo
        console.log(prototypeUrl);
        const iframe = document.getElementById("prototype");
        iframe.src = prototypeUrl;
        iframe.style.display = "block";
      } else if (imgPath && imgPath !== "null") {
        // Mostrar la imagen
        const imgElement = document.getElementById("img_interes");
        imgElement.src = imgPath;
        imgElement.style.display = "block";
      }
    })
    .catch((error) =>
      console.error("Error al cargar la configuración desde /api/config:", error)
    );
});

function enviarPuntos(puntos) {
  fetch("/api/save-points", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ points: puntos, id: parseInt(id, 10) }),
  })
    .then((response) => response.text())
    .then((result) => {
      console.log(result);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function enviarTaskLogIndividual(taskLog) {
  fetch("/api/save-tasklogs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      taskLogs: [taskLog],
      subject_id: parseInt(id, 10),
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      console.log("TaskLog enviado:", result);
    })
    .catch((error) => {
      console.error("Error al enviar TaskLog:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/tasks")
    .then((response) => response.json())
    .then((tasks) => {
      tasksArray = tasks.tasks;

      console.log(tasksArray);
    })
    .catch((error) =>
      console.error("Error al cargar las tareas desde /api/tasks:", error)
    );

  // Botón para abrir la barra
  document.getElementById("toggle-bar").addEventListener("click", function () {
    document.getElementById("task-bar").style.display = "block";
  });

  // Botón para cerrar la barra
  document.getElementById("close-bar").addEventListener("click", function () {
    document.getElementById("task-bar").style.display = "none";
  });

  // Manejar el envío de la respuesta
  document
    .getElementById("task-bar-submit")
    .addEventListener("click", function () {
      const userInput = document.getElementById("task-bar-input").value;

      taskLogs[currentTaskIndex].endTime = new Date().toLocaleString("en-US", {
        timeZone: "America/Argentina/Buenos_Aires",
      });
      taskLogs[currentTaskIndex].response = userInput;

      enviarTaskLogIndividual(taskLogs[currentTaskIndex]);

      console.log(
        `Respuesta a "${tasksArray[currentTaskIndex]}": ${userInput}`
      );
      currentTaskIndex++;
      document.getElementById("task-bar-input").value = ""; // Limpiar el input
      showNextTaskInBar(); // Mostrar la siguiente tarea
    });

  document.getElementById("skip-button").addEventListener("click", function () {
    // Aquí puedes agregar la lógica para omitir la tarea actual

    taskLogs[currentTaskIndex].endTime = new Date().toLocaleString("en-US", {
      timeZone: "America/Argentina/Buenos_Aires",
    });
    taskLogs[currentTaskIndex].response = "skipped"; // Opción de omitir

    enviarTaskLogIndividual(taskLogs[currentTaskIndex]);

    document.getElementById("task-bar-input").value = ""; // Limpiar el input
    console.log("Tarea omitida");
    currentTaskIndex++;
    showNextTaskInBar(); // Mostrar la siguiente tarea
  });
});

let startTime = null;

document.addEventListener("DOMContentLoaded", function () {
  // Botón para abrir la barra
  document.getElementById("toggle-bar").addEventListener("click", function () {
    const taskBar = document.getElementById("task-bar");
    const prototype = document.getElementById("prototype");

    taskBar.classList.add("visible");
    taskBar.style.display = "block";

    document.getElementById("toggle-bar").style.display = "none";

    prototype.style.pointerEvents = "none";
    prototype.style.filter = "blur(5px)";

    if (!startTime) {
      startTime = new Date().toLocaleString("en-US", {
        timeZone: "America/Argentina/Buenos_Aires",
      });
      console.log("Tiempos de inicio:", startTime);
    }

    if (currentTaskIndex === 0 && tasksArray.length > 0) {
      showNextTaskInBar();
    }
  });

  // Botón para cerrar la barra
  document.getElementById("close-bar").addEventListener("click", function () {
    const taskBar = document.getElementById("task-bar");
    const prototype = document.getElementById("prototype");

    taskBar.classList.remove("visible");
    taskBar.style.display = "none";

    document.getElementById("toggle-bar").style.display = "block";

    prototype.style.pointerEvents = "auto";
    prototype.style.filter = "none";
  });
});

let tasksArray = []; // Inicializa como un arreglo vacío
let taskLogs = []; // Inicializa como un arreglo vacío

function showNextTaskInBar() {
  console.log(taskLogs);
  const taskBarInput = document.getElementById("task-bar-input");

  if (currentTaskIndex < tasksArray.length) {
    const taskText = tasksArray[currentTaskIndex].task;
    const taskType = tasksArray[currentTaskIndex].type;

    // Registrar el tiempo de inicio de la tarea actual
    taskLogs[currentTaskIndex] = {
      startTime:
        currentTaskIndex === 0
          ? startTime // Usar el tiempo global si es la primera tarea
          : new Date().toLocaleString("en-US", {
              timeZone: "America/Argentina/Buenos_Aires",
            }),
      endTime: null,
      response: null,
    };

    document.getElementById("task-bar-text").innerText = taskText;

    if (taskType === "bool") {
      taskBarInput.style.display = "none"; // Oculta el input
    } else {
      taskBarInput.style.display = "block"; // Muestra el input
    }
  } else {
    window.location.href = "/fin-medicion";
  }
}

function checkCalibrationAndShowButton() {
  if (isCalibrated()) {
    const toggleBar = document.getElementById("toggle-bar");
    toggleBar.style.display = "block";

    // Mostrar la primera tarea en la barra
    if (tasksArray.length > 0) {
      currentTaskIndex = 0; // Inicializar el índice de tareas
    } else {
      console.error("No hay tareas disponibles para mostrar.");
    }
  }
}

// Ocultar el botón de tarea inicialmente
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("toggle-bar").style.display = "none";
});
