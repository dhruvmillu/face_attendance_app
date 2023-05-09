console.log("hello world")


video = document.getElementById("videoElement"); // video is the id of video tag

console.log(video)

if (navigator.mediaDevices.getUserMedia) {
    console.log("mediaDevices.getUserMedia supported");
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function (stream) {
        video.srcObject = stream;
      })
      .catch(function (err0r) {
        console.log("Something went wrong!");
      });
  }