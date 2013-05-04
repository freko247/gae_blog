gae_blog
========

An evolved version of the guestbook example in the 'getting started' tutorial on the Google App Engine homepage (https://developers.google.com/appengine/docs/python/gettingstartedpython27/).

Blog could be desrcibed as minimalistic, with co-writer support.

Application uses the 52framework for layout, all credit to them.


Install
=======
- Download repository
- Create app.yaml (described in followig paragraph)
- Upload application (https://developers.google.com/appengine/docs/python/gettingstartedpython27/uploading)

app.yaml
--------
Add following to app.yaml, where <youraplicationname> is replaced with the application name you have registered.

    application: <yourapplicationname>
    version: 1
    runtime: python27
    api_version: 1
    threadsafe: yes
    
    handlers:
    - url: /css
      static_dir: css
    
    - url: /graphics
      static_dir: graphics
    
    - url: /.*
      script: freko247.app
    
    libraries:
    - name: jinja2
      version: latest
