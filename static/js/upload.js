document.addEventListener("DOMContentLoaded", () => {

    const uploadButton = document.getElementById(
        "uploadButton"
    );

    const uploadFile = document.getElementById(
        "uploadFile"
    );

    const uploadMessage = document.getElementById(
        "uploadMessage"
    );


    if (
        !uploadButton ||
        !uploadFile ||
        !uploadMessage
    ) {
        return;
    }



    uploadButton.addEventListener(
        "click",
        async () => {


            const file = uploadFile.files[0];


            if (!file) {

                uploadMessage.innerHTML = `

                    <div class="alert alert-danger">

                        Please select a file first.

                    </div>

                `;

                return;

            }



            const formData = new FormData();


            formData.append(
                "file",
                file
            );



            uploadButton.disabled = true;


            uploadButton.textContent =
                "Uploading...";



            try {


                const response = await fetch(
                    "/api/verbal-autopsy/upload",
                    {

                        method: "POST",

                        body: formData

                    }
                );



                const result = await response.json();



                if (response.ok) {


                    const summary =
                        result.summary;


                    let errorsHtml = "";



                    if (
                        summary.errors &&
                        summary.errors.length > 0
                    ) {


                        errorsHtml = `

                            <hr>

                            <h6>
                                Validation Errors
                            </h6>

                        `;


                        summary.errors.forEach(
                            (error) => {


                                errorsHtml += `

                                    <div class="mb-3">

                                        <strong>
                                            Row:
                                        </strong>
                                        ${error.row}
                                        <br>


                                        <strong>
                                            Patient ID:
                                        </strong>
                                        ${
                                            error.patientid || 
                                            "Not provided"
                                        }


                                        <ul>

                                `;


                                error.errors.forEach(
                                    (message) => {

                                        errorsHtml += `

                                            <li>
                                                ${message}
                                            </li>

                                        `;

                                    }
                                );


                                errorsHtml += `

                                        </ul>

                                    </div>

                                `;


                            }
                        );

                    }



                    uploadMessage.innerHTML = `

                        <div class="alert alert-success">

                            <h6>
                                Upload completed successfully.
                            </h6>


                            <hr>


                            <p class="mb-1">
                                Total Rows:
                                <strong>
                                    ${summary.total_rows}
                                </strong>
                            </p>


                            <p class="mb-1">
                                Inserted:
                                <strong>
                                    ${summary.inserted}
                                </strong>
                            </p>


                            <p class="mb-1">
                                Updated:
                                <strong>
                                    ${summary.updated}
                                </strong>
                            </p>


                            <p class="mb-1">
                                Duplicates:
                                <strong>
                                    ${summary.duplicates}
                                </strong>
                            </p>


                            <p class="mb-1">
                                Invalid:
                                <strong>
                                    ${summary.invalid}
                                </strong>
                            </p>


                            ${errorsHtml}


                        </div>

                    `;


                    setTimeout(
                        () => {

                            window.location.reload();

                        },

                        8000
                    );


                } else {


                    uploadMessage.innerHTML = `

                        <div class="alert alert-danger">

                            ${result.message}

                        </div>

                    `;


                }



            } catch (error) {


                uploadMessage.innerHTML = `

                    <div class="alert alert-danger">

                        Upload failed. Please try again.

                    </div>

                `;


            }



            uploadButton.disabled = false;


            uploadButton.textContent =
                "Upload";


        }
    );


});