# realm-transcription

This repository is an experiment in abandoning my initial production concept (deploying on banana.dev), and deploying on a more robust service, like paperspace gradient deployments (which is run by Digital Ocean). I was able to get this workflow working, and – while it leaves a bit to be desired, the reliability seems way better than our friends at banana.

## Steps 

The basic workflow here is: create a docker image and push it docker hub, build a deployment off of that image in paperspace gradient. This is fairly straight-forward – the only complexity is that you need a nvidia-cuda enabled machine to build the docker image, so that all of the cuda runtime is included in the image. Luckily, we can use paperspace for this, too. Note, it's 1:00am EST, so I'm going to scrawl these notes quickly, and clean them up later.

> TODO(Nic): Make all of this into a script, or better yet a Github action that fires when you push to `main`.

### 0. Pre-reqs.

1. You need a Paperspace account. Make one. It will need a payment method, as we're going to spin up GPUs.
2. You need a docker hub account. Make one. You do not need to pay for it – all our images can be public. A todo is to figure out how to deploy private images, but right now, we're just deploying open source stuff anyway.
### 1. Create a Docker Image

1. Log into Paperspace and navigate to the paperspace CORE product. These are the bare-metal machines. We will temporarily provision a GPU-enabled box to help us build the image. Spin up a new machine, and make sure it has an Nvidia GPU. Choose the `ML-in-a-box` option; this is pre-configured with all the libraries and drivers that the paperspace racks need – this ensures compatibility with the Gradient Deployment that this image will ultimately be placed on. Any nvidia GPU will do.

2. Set up ssh for the box. You can do this with a password, or a key. This will be a short-lived instance that we'll destroy after the deploying the image, so don't worry about security too much.

3. ssh into this box.

4. Clone this repository into the box.

5. `sudo nvidia-docker build -t nicschumann/lullaby-realm-transcription-gradient:latest .` The `nicschumann/lullaby-realm-transcription-gradient` can really be anything you want. We're going to push this to docker hub later. This will build the container, and will probably take around 300s.

6. `sudo nvidia-docker push nicschumann/lullaby-realm-transcription-gradient:latest`. This pushes the docker image to the docker hub. The image is like 7gb at least, so it'll take some time. Luckily paperspace has pretty good network speeds.

7. Once this is done, you should be all set. Maybe verify that the image made it to docker hub.

8. Disable this GPU instance, otherwise you'll get billed a lot.

### 2. Deploy to Gradient

1. Log into paperspace and navigate to the Gradient product. Create a new project.

2. Inside the project, navigate to the deployments tab. Click create. 

3. Name the deployment, choose a nice GPU. I have tested this code on `P4000` (it doesn't work), and `RTX4000` (it works). More fancy GPUs require paying a monthly fee, which I'll consider. For now, `RTX4000` seems fine for testing and development.

4. Set replicas to `1` for now. This is where we can autoscale or manually scale the number of instances. Load balancing is automatically applied. Setting the replicas to 0 disables the deployment, and turns off billing.

5. Put the name of the image you built before into the `Image` field. For this example, it's `nicschumann/lullaby-realm-transcription-gradient`.

6. Set the port to `80`

7. Click `Deploy`. It should build successfully and deploy in a few minutes. Once it's ready, grab the url, and update the `MODEL_URL` in `.env.secret` in your gateway server instance to start using this microservice in your development.

> NOTE(Nic): Make sure to put as much of this as you can into configuration files that we can leverage with the paperspace command line tool. This is a todo for this repo.

The end for now

