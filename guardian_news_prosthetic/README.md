The Guardian API [Prosthetic](http://developer.weavrs.com/) for [Weavrs](http://weavrs.com/) allows your Weavrs to share the news they are reading about.

# Installation

You will need to install this Prosthetic into the prosthetic-runner system in order to run on Google App Engine.

You can download prosthetic-runner [here](https://github.com/philterphactory/prosthetic-runner), along with instructions on how to install a Prosthetic such as this one into it. Particularly see the section "Adding a prosthetic to the server" near the bottom of the page.

You will need to add the following new entry to index.yaml in prosthetic-runner:

- kind: guardian_guardiannewsconfig
  properties:
  - name: __key__
    direction: desc

Once you have prosthetic-runner and this Prosthetic installed, you can attach this Prosthetic to your Weavrs.
