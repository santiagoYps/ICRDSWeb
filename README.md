# Intelligent Collision Risk Detection System (ICRDS) Web 
Web platform developed in Flask for the manipulation and visualization of the kinematic data captured by the collection devices. 
In addition, it has the development of a Machine Learning model that allows classifying the areas where Near-Crashes events can occur [[1]](https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/dot_hs_811_382.pdf).

## Preview
<p>
  <img src="https://bnz05pap001files.storage.live.com/y4mjuQp-6esgGPj5nP9AWr5p1Oixc2ToKY9uaa0skhMVR546AmeLQFRQ-OEl-mazj4VinqcXfZKeS_Bztt992gkZl9wVNaJFmnRdC8H99YK7ptQBK64ZxMA0VmUIPYntJDHRQJq-deLgm06gssG4ioQPtKdlFPyZ57Dgmm6dmO-cYfLlpkaRmssHWEVmZIPsyDK?width=1024&height=546&cropmode=none" width="250"></img>
  <img src="https://bnz05pap001files.storage.live.com/y4m83Gp0uzOLKO4VEpDJKclj96mnmg0zf-uW8imCaE7MgcptWgSNqcUyHHtMgV6KuIxeS-mXZtjGxfqInpT_lYeH71GSAqlY0OsRwdUhGagYq5NEygsqGLh5zbSG3_RMd5AqVglHOd17owe2cUbZqsFO-aH5sOWVpV2Fai4yUPnGrNbiSQa0aNF1hffjcTCWXYT?width=1366&height=728&cropmode=none" width="250"></img>
  <img src="https://bnz05pap001files.storage.live.com/y4mGW9m-5Dz-wuWVzB5arlWKuAyCcbfZPGW0NKCV4P6kNFlshO5Yognevh9G3G5poNepNmmNT3HuU5RF2DHOklotXWattRQsEqqb-V4DlvdsCBPqw2cR03kvWQ8xuSptFBOrjiBQgvmLWjcImtT4lbjXdh4oVacO_I8UQEqN9yBbYLFAS2cd7iTlYdZUWHG4TIl?width=1366&height=728&cropmode=none" width="250"></img>
</p>
<p>
  <img src="https://bnz05pap001files.storage.live.com/y4mTG8GpfeXS_aJexFBCGhVSeH1QkakymSHNg_TDPwVnTOsvAIGO3iQtvwJdVr2glCz6iSS9tD6HZceCD3onEiZHffCXmLUd1O0kPbwHtoPTyVuYUJOTBm_5V1gAPLX9yOdmJRF9h9bKPQrowzS_ERJHwlkoIKssDx0cYTD94mGBClA-9bCiO9lRZrJhZP-Gcl-?width=1366&height=768&cropmode=none" width="250"></img>
  <img src="https://bnz05pap001files.storage.live.com/y4mSdma-AVaP3sE3eRuvTj2gv8pBIyuMYt5eFsD7GLkbiw6M2o-aWnugX_6dgP0xe2rgvJNuRA-FeTAZqIus5RKcvonO6-BeOX1BjSRoTIU1YL6Fm7eoUldjeAtRzQkDk3xL2C7H-z4tSZoew-uKTLtvNxNUdh6t3Igm1P_Sfq0WVKSsZSSIYU9ZHzlW58hMrsC?width=1366&height=728&cropmode=none" width="250"></img>
  <img src="https://bnz05pap001files.storage.live.com/y4md_A7qkxwriqyV03FGlBHUHULm0OQq82XopBRHmczPhPXz07lSCbr19XCQNgSXdgghk5RNYVJ8QhPP25ueB_PC73TTdsOETPERlNtva6fq9AV5HftqvK9mMJSWNj431dpreueOD66mFtQHMCbTNwfffh2Qdm9CaG95jEJzn4DIppRCx-hcHb8gQfVwG6GhjqS?width=1366&height=728&cropmode=none" width="250"></img>
</p>

## Installation
1. Clone repository.
2. Install Conda on your machine.
3. Install conda enviroment, run: `conda env create -f tesis.yml`, more info in [Conda Documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file).
4. Active conda enviroment, run: `conda activate tesis`.
5. Initialize Flask Application, run: `flask run`.

### Note:
You need to setup your .flaskenv file and .env file, these should look like this:
```bash
#.flaskenv
FLASK_ENV=development
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=3000
```
It contains the access credentials to firebase, *for security reasons these credentials must be 
created by you in your firebase client*, a [tutorial here](https://firebase.google.com/docs/admin/setup). The .env configuration file should look something like this
(All information can be extracted from the file: "service-account-file.json"):
```bash
TYPE="service_account"
PROJECT_ID="YOUR_PROJECT_ID"
PRIVATE_KEY_ID="YOUR_KEY_ID"
PRIVATE_KEY="YOUR_PRIVATE_KEY"
CLIENT_EMAIL="YOUR_CLIENT_EMAIL"
CLIENT_ID="YOUR_CLIENT_ID"
AUTH_URI="YOUR_AUTH_URI"
TOKEN_URI="YOUR_TOKEN_URI"
AUTH_PROVIDER_X509_CERT_URL="YOUR_AUTH_PROVIDER_X509_CERT_URL"
CLIENT_X509_CERT_URL="YOUR_CLIENT_X509_CERT_URL"
```

## Usage
In your web browser type http://localhost:3000/ and start browsing the platform (the URL depends on the configuration made in .flaskenv).

In In the ["machine_learning"](./machine_learning) folder are the jupyter files used in the development of the Machine Learning algorithm

## Requirementes
All libraries are specified in the [tesis.yml](./tesis.yml) file.

# Authors adn Contact
[Juan Jose Paredes Rosero](https://www.linkedin.com/in/juan-paredes-a624aa186/), [Santiago Felipe Yepes](https://www.linkedin.com/in/santiagoyps)
