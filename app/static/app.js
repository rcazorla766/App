document.addEventListener("DOMContentLoaded", () => {

    const predictButton = document.getElementById("predict-button");

    predictButton.addEventListener("click", async () => {

        // Construir el JSON con los datos del formulario
        const predictionRequest = {

            MedInc: Number(document.getElementById("MedInc").value),
            HouseAge: Number(document.getElementById("HouseAge").value),
            AveRooms: Number(document.getElementById("AveRooms").value),
            AveBedrms: Number(document.getElementById("AveBedrms").value),
            Population: Number(document.getElementById("Population").value),
            AveOccup: Number(document.getElementById("AveOccup").value),
            Latitude: Number(document.getElementById("Latitude").value),
            Longitude: Number(document.getElementById("Longitude").value)

        };

        try {

            const response = await fetch("/predict", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(predictionRequest)

            });

            if (!response.ok) {
                throw new Error("Prediction request failed");
            }

            const result = await response.json();

            document.getElementById("prediction-result").innerHTML =
                `<strong>Prediction:</strong> ${result.prediction}<br>
                 <strong>Model version:</strong> ${result.model_version}`;

        }
        catch (error) {

            document.getElementById("prediction-result").innerHTML =
                `<span style="color:red;">Error performing prediction.</span>`;

            console.error(error);

        }

    });

});