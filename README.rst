Qtazu
=====

Python Qt widgets for `CG-Wire <https://www.cg-wire.com/>`__ using
```gazu`` <https://github.com/cgwire/gazu>`__.

Dependencies
------------

This requires `Gazu <https://github.com/cgwire/gazu>`__ and
`Qt.py <https://github.com/mottosso/Qt.py>`__.

What is Qtazu?
--------------

*Qtazu* implements Qt widgets to connect and work with a CG-Wire
instance through an interface running in Python.

-  Reusable components to develop your own interfaces to interact with
   CG-Wire.
-  Embeddable in DCCs supporting Python and Qt
-  *Or* use them in your own standalone Python application, like a
   studio pipeline.
-  Agnostic widgets so you can easily instantiate them as you need
-  Support PyQt5, PySide2, PyQt4 and PySide through
   ```Qt.py`` <https://github.com/mottosso/Qt.py>`__

**WIP**: *This is a WIP repository*

Examples
--------

The Widgets initialize in such a way you can easily embed them for your
needs.

*The examples assume a running Qt application instance exists.*

Logging in
~~~~~~~~~~

.. figure:: https://user-images.githubusercontent.com/2439881/70457311-3ab92580-1ab0-11ea-817f-97b43d749923.png
   :alt: qtazu\_login

   qtazu\_login

.. code:: python

    from qtazu.widgets.login import Login

    widget = Login()
    widget.show()

If you want to set your CG-Wire instance URL so the User doesn't have to
you can set it through environment variable: ``CGWIRE_HOST``

.. code:: python

    from qtazu.widgets.login import Login
    import os

    os.environ["CGWIRE_HOST"] = "https://zou-server-url/api"
    widget = Login()
    widget.show()

Directly trigger a callback once someone has logged in using Qt signals:

.. code:: python

    from qtazu.widgets.login import Login

    def callback(success):
        print("Did login succeed? Answer: %s" % success)

    widget = Login()
    widget.logged_in.connect(callback)
    widget.show()

You can also automate a `login through
``gazu`` <https://github.com/cgwire/gazu#quickstart>`__ and ``qtazu``
will use it.

Or if you have logged in through another Python process you can pass on
the tokens:

.. code:: python

    import os
    import json

    # Store CGWIRE_TOKENS for application (simplified for example)
    os.environ["CGWIRE_TOKENS"] = json.dumps(gazu.client.tokens)
    os.environ["CGWIRE_HOST"] = host


    # In application "log-in" using the tokens
    host = os.environ["CGWIRE_HOST"]
    tokens = json.loads(os.environ["CGWIRE_TOKENS"])
    gazu.client.set_host(host)
    gazu.client.set_tokens(tokens)

Submitting Comments
~~~~~~~~~~~~~~~~~~~

You can easily submit comments for a specific Task, this includes drag
'n' dropping your own images of videos as attachment or using a Screen
Marguee tool to attach a screenshot to your comment.

*Make sure you are logged in prior to this.*

.. code:: python

    from qtazu.widgets.comment import CommentWidget

    task_id = "xyz" # Make sure to set a valid Task Id
    widget = CommentWidget(task_id=task_id)
    widget.show()

.. figure:: https://user-images.githubusercontent.com/2439881/70453939-ec088d00-1aa9-11ea-876b-38747ee16b13.gif
   :alt: qtazu\_comment\_screenshot

   qtazu\_comment\_screenshot

Display all Persons with Thumbnails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's easy and quick to embed the available Persons into your own list
view.

.. figure:: https://user-images.githubusercontent.com/2439881/70457319-3bea5280-1ab0-11ea-97b9-46c1388eb452.png
   :alt: qtazu\_persons\_model

   qtazu\_persons\_model

.. code:: python

    from qtazu.models.persons import PersonModel
    from Qt import QtWidgets, QtCore

    model = PersonModel()
    view = QtWidgets.QListView()
    view.setIconSize(QtCore.QSize(30, 30))
    view.setStyleSheet("QListView::item { margin: 3px; padding: 3px;}")
    view.setModel(model)
    view.setMinimumHeight(60)
    view.setWindowTitle("CG-Wire Persons")
    view.show()

Here's an example prototype of listing Persons as you tag them:

.. figure:: https://user-images.githubusercontent.com/2439881/70454197-57525f00-1aaa-11ea-8a07-85e4b16cf12d.gif
   :alt: qtazu\_tag\_prototype\_02

   qtazu\_tag\_prototype\_02

Define your own Qt widget that loads Thumbnails in the background
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will show all CG-Wire projects as thumbnails.

.. figure:: https://user-images.githubusercontent.com/2439881/70457323-3db41600-1ab0-11ea-9488-720370a0f757.png
   :alt: qtazu\_projects

   qtazu\_projects

.. code:: python

    import gazu
    from Qt import QtWidgets
    from qtazu.widgets.thumbnail import ThumbnailBase

    main = QtWidgets.QWidget()
    main.setWindowTitle("CG-Wire Projects")
    layout = QtWidgets.QHBoxLayout(main)

    for project in gazu.project.all_open_projects():
       
        thumbnail = ThumbnailBase()
        thumbnail.setFixedWidth(75)
        thumbnail.setFixedHeight(75)
        thumbnail.setToolTip(project["name"])
        project_id = project["id"]
        thumbnail.load("pictures/thumbnails/projects/{0}.png".format(project_id))
        layout.addWidget(thumbnail)
        
    main.show()

Welcome a User with a message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Show a Welcome popup to the user with his or her thumbnail.

.. figure:: https://user-images.githubusercontent.com/2439881/70457328-3e4cac80-1ab0-11ea-9b4f-6ceccf2183d0.png
   :alt: qtazu\_welcome\_popup

   qtazu\_welcome\_popup

.. code:: python

    from Qt import QtWidgets, QtGui, QtCore
    from qtazu.widgets.thumbnail import ThumbnailBase
    import gazu


    class UserPopup(QtWidgets.QWidget):
        """Pop-up showing 'welcome user' and user thumbnail"""
        def __init__(self, parent=None, user=None):
            super(UserPopup, self).__init__(parent=parent)
        
            layout = QtWidgets.QHBoxLayout(self)
       
            thumbnail = ThumbnailBase()
            thumbnail.setFixedWidth(75)
            thumbnail.setFixedHeight(75)
            thumbnail.setToolTip(user["first_name"])
            
            welcome = QtWidgets.QLabel("Welcome!")
            
            layout.addWidget(thumbnail)
            layout.addWidget(welcome)
        
            self.thumbnail = thumbnail
            self.welcome = welcome
            self._user = None
            
            if user:
                self.set_user(user)
        
        def set_user(self, user):
            
            self._user = user
            
            # Load user thumbnail 
            self.thumbnail.load("pictures/thumbnails/persons/{0}.png".format(user["id"]))
            
            # Set welcome message
            self.welcome.setText("Welcome {first_name} {last_name}!".format(
                **user
            ))


    # Show pop-up about current user
    user = gazu.client.get_current_user()
    popup = UserPopup(user=user)
    popup.show()
