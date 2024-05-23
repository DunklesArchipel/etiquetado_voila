import glob
import os
import yaml

import time
from pathlib import Path, PurePath

from ipywidgets import widgets, HBox, VBox, Layout
from etiquetado_voila.apps.fileobserver import FileObserver


class OptionsWidget():

    def __init__(self, dir,
        suffix=None,
        option_selector=None,
        file_observer=None
    ):
        self._dir = dir
        self._suffix=suffix

        self.option_selector = option_selector or widgets.SelectMultiple(
                description=f"Files",
                layout=Layout(width="600px", height="180px", flex="flex-grow"),
            )

        self.file_observer = file_observer or FileObserver(observed_dir=self._dir, suffix=self._suffix)

        # self.text_box_folder_path.observe(self.template_observer.on_text_value_changed, names="value")

    def on_file_created(self, *args, **kwargs):
        return self.file_observer.on_file_create(*args, **kwargs)

    def on_file_deleted(self, *args, **kwargs):
        return self.file_observer.on_file_delete(*args, **kwargs)

    @property
    def files(self):
        return [PurePath(file) for file in glob.glob(os.path.join(self._dir, f"**{self._suffix}"))]

    def add_file(self, _, filename):
        self.update_files(_, filename)
        # Set selection to last element added
        # self.option_selector.value = [option for option in self.option_selector.options if Path(filename).stem in str(option)][0]

    def update_files(self, _, filename):
        self.option_selector.options = self.files


class ListOptions(OptionsWidget):

    def __init__(self, dir, suffix=None, option_selector=None, file_observer=None):
        option_selector = option_selector or  widgets.SelectMultiple(
            description=f"Tagged Files",
            layout=Layout(width="600px", height="180px", flex="flex-grow"),
        )
        OptionsWidget.__init__(self, dir=dir, suffix=suffix, option_selector=option_selector, file_observer=file_observer)

        self.option_selector.options = self.files

        self.file_observer.start()
        self.on_file_created(self.add_file)
        self.on_file_deleted(self.update_files)


class MetadataOptions(OptionsWidget):

    def __init__(self, dir, suffix=None, option_selector=None, file_observer=None):
        option_selector = option_selector or  widgets.Dropdown(
            description=f"Yaml templates",
            layout=Layout(width="600px", height="180px", flex="flex-grow"),
        )
        OptionsWidget.__init__(dir=dir, suffix=suffix, option_selector=option_selector, file_observer=file_observer)


class ListOptions2(OptionsWidget):
    r"""Keep the content of a selection widget up to date with content in a file.
    This allows storing the state of the widget in, for example, a yaml file
    when you want to pick up the work at a later stage.
    """

    def __init__(
        self, option_selector=None,
        widget_state_file="widget_states.yaml",
        widget_name=None,
        suffix=None,
        file_observer=None,
        dir=None
    ):

        self._widget_state_file = widget_state_file
        self.widget_name = widget_name or self.__class__.__name__

        self.option_selector = option_selector or widgets.SelectMultiple(
            description=f"{self.widget_name}",
            layout=Layout(width="600px", height="180px", flex="flex-grow"),
        )

        OptionsWidget.__init__(self, dir=dir, suffix=suffix, option_selector=option_selector, file_observer=file_observer)

        self.sync_options()
        self.on_file_created(self.add_option)
        self.on_file_deleted(self.remove_option)

    @property
    def widget_state_file(self):
        if not os.path.exists(self._widget_state_file):
            with open(self._widget_state_file, "w") as f:
                f.write(f"{self.widget_name}: []\n")
        return self._widget_state_file

    def add_option(self, _, option):
        new_options = [item for item in self.option_selector.options]
        if not new_options:
            new_options.append(option)
        if not option in new_options:
            new_options.append(option)
        self.reset_options(new_options)

    def remove_option(self, _, option):
        new_options = [item for item in self.option_selector.options if item != option]
        self.reset_options(new_options)

    def reset_options(self, options):
        self.option_selector.options = options
        file_metadata = self.file_metadata
        file_metadata[self.widget_name] = options
        # tagged = {self.widget_name: options}
        with open(self.widget_state_file, "w") as f:
            yaml.dump(file_metadata, f)

    def sync_options(self):
        file_options = self.get_file_options()
        widget_options = self.option_selector.options

        new_options = list(set(file_options) | set(widget_options))

        # new_options = [_ for _ in self.tagged_files.options if not _ in self.tagged_files.value]
        self.reset_options(new_options)

    @property
    def file_metadata(self):
        with open(self.widget_state_file, "rb") as f:
            file_metadata = yaml.load(f, Loader=yaml.SafeLoader)
        return file_metadata

    def get_file_options(self):
        metadata = self.file_metadata
        metadata.setdefault(self.widget_name, [])
        return metadata[self.widget_name]


    #############################

class ListOptions3:
    r"""Keep the content of a selection widget up to date with content in a file.
    This allows storing the state of the widget in, for example, a yaml file
    when you want to pick up the work at a later stage.
    """

    def __init__(
        self, option_selector=None, widget_state_file="widget_states.yaml", widget_name=None
    ):

        self._widget_state_file = widget_state_file
        self.widget_name = widget_name or self.__class__.__name__

        self.option_selector = option_selector or widgets.SelectMultiple(
            options=(""),
            description=f"{self.widget_name}",
            layout=Layout(width="600px", height="180px", flex="flex-grow"),
        )

        self.sync_options()

    @property
    def widget_state_file(self):
        if not os.path.exists(self._widget_state_file):
            with open(self._widget_state_file, "w") as f:
                f.write(f"{self.widget_name}: []\n")
        return self._widget_state_file

    def add_option(self, option):
        new_options = [item for item in self.option_selector.options]
        if not new_options:
            new_options.append(option)
        if not option in new_options:
            new_options.append(option)
        self.reset_options(new_options)

    def remove_option(self, option):
        new_options = [item for item in self.option_selector.options if item != option]
        self.reset_options(new_options)

    def reset_options(self, options):
        self.option_selector.options = options
        file_metadata = self.file_metadata
        file_metadata[self.widget_name] = options
        # tagged = {self.widget_name: options}
        with open(self.widget_state_file, "w") as f:
            yaml.dump(file_metadata, f)

    def sync_options(self):
        file_options = self.get_file_options()
        widget_options = self.option_selector.options

        new_options = list(set(file_options) | set(widget_options))

        # new_options = [_ for _ in self.tagged_files.options if not _ in self.tagged_files.value]
        self.reset_options(new_options)

    @property
    def file_metadata(self):
        with open(self.widget_state_file, "rb") as f:
            file_metadata = yaml.load(f, Loader=yaml.SafeLoader)
        return file_metadata

    def get_file_options(self):
        metadata = self.file_metadata
        metadata.setdefault(self.widget_name, [])
        return metadata[self.widget_name]
