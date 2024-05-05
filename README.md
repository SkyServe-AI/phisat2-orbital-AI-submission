# Orbital-ai-phisat2-skyserve
Onboard detection dataset model and artefacts.

## Instructions
1. Get dataset for training in the current directory with this [download link](https://zenodo.org/records/5095024/files/sentinel2_cloudmask_kz.zip?download=1) with dataset reading material [here](https://zenodo.org/records/5095024).
2. Run the training notebook for training different model versions [here](SkyServe_Hosted_Notebook_Orbital_AI_challenge_PhiSat_2.ipynb). Make sure that local address of the dataset is right.
3. Jetson run scripts: The optimized tflite model for testing inference runtimes is hosted [here](oai-jetson-testrun). Setup the environment with the requirements file [here](oai-jetson-testrun\requirements.txt). You can run the `test_run.py` script for the same. 
4. Satellite simulation scripts: The satellite groundtrack simulations against the road density datasets can be found [here](). Unzip the road density [image](satellite_simulation_road_density\grip4_area_land_km2_georeference.zip) in the same folder. Update your spacetrack username and password in the [main file](satellite_simulation_road_density\main.py). Run main.py to generate the revisit images. 
