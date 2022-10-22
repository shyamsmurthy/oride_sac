# oride_sac
Code for ORide attack

The file attack.py consists of the rider's location harvesting attack on ORide[1].

The code (written in Python) uses Google Maps API and the UTM library for python.
Due to reasons of confidentiality, we are unable to provide our API key along with the code.

The API key is necessary for using Google Map API's services. The API key is linked with a billing account,
and can be set up by following the instructions here:
https://developers.google.com/maps/documentation/javascript/get-api-key

For our code, we use the Road API and Distance-Matrix API, and these need to be activated from the 
Google Cloud Platform Console. 

[1] A. Pham, I. Dacosta, G. Endignoux, J. Troncoso-Pastoriza, K. Huguenin, and J.-P. Hubaux. ORide: A Privacy-Preserving yet Accountable Ride-Hailing Service. In Proceedings of the 26th USENIX Security Symposium, Vancouver, BC, Canada, August 2017.
