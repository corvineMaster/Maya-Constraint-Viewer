# Maya-Constraint-Viewer
A tool for viewing all constrained objects in the scene, along with the constriants themselves and the parent objects weighted to them

To run the tool, `save constraint_viewer.py` to your default Maya scripts folder, then run the following code in a python tab of the Maya script editor:
```
from constraint_viewer import constraintViewer
constraintViewer.show_dialog()
```

By default, the window will show all the objects that are constrained in the scene. If an item is selected in the To filter what you see in the window, you can choose a specific type of constraint in the drop down menu, as well as filter by name in the search bar. Additionally, you can click the search button to populate the search bar based on what's currently selected in the outliner.

If you click on the drop down button of any of the items in the tree list, you'll see their constraint object and all the objects that are constraining them. Double click on any of these objects to select them in the outliner. If anything has changed in the scene, clicking the refresh button will refresh what's shown in the tree list.

If you want to create a new constraint, clicking the options button will bring up the default options box for the type of constraint currently listed in the drop down menu. This button is disabled if "All" is currently selected.
