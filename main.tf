provider "google" {
  project = "project-66fac5e9-c904-4bfc-907"
  region  = "us-east1-b"
}

resource "google_compute_instance" "buscafri" {
  name         = "buscafri"
  machine_type = "e2-micro"
  zone         = "us-east1-b"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 30
    }
  }

  network_interface {
    network = "default"
    access_config {
      // IP público será atribuído automaticamente
    }
  }

  # Script de automação que será executado no boot
  metadata_startup_script = file("scripts/setup_vps.sh")
  
  tags = ["http-server", "https-server"]
}
