class VariableMetadata:

    def __init__(self, variable_metadata=None):

        self.metadata_text_fields = None

        if variable_metadata:
            self.metadata_text_fields = [
                widgets.Text(description=key, value=value, continuous_update=False)
                for key, value in variable_metadata.items()
            ]

    @property
    def variable_metadata(self):
        # returns the name/description of the text fields and the current values
        return self.metadata_text_fields or {text_field.description: text_field.value for text_field in self.metadata_text_fields}

class AutoQuetadoVarMetadata:

    def __init__(
        self,
        observed_dir,
        suffix,
        template_dir,
        update_metadata=None, # method that changes metadata received from YAML or adds new metadata
        variable_metadata=None,
        template_suffix=".yaml",
    ):
        self._update_metadata = update_metadata

        self._template_dir = template_dir
        self._template_suffix = template_suffix

        self._variable_metadata = variable_metadata

        self.output = widgets.Output()

        self.foa = FileObserverApp(
            observed_dir=observed_dir,
            suffix=suffix,
            output=self.output
        )

        self.on_file_created(self.tag_data)
        # self.on_file_created(lambda _, filename: print(filename))

        self.metadata_app = MetadataApp(
            template_dir=self._template_dir, template_suffix=self._template_suffix, update_metadata=update_metadata, variable_metadata=variable_metadata
        )

        self.metadata_app.dropdown_yaml.observe(
            self.foa.on_text_value_changed, names="value"
        )
        if self._variable_metadata:
            for text in self.metadata_app.metadata_text_fields:
                text.observe(self.foa.on_text_value_changed, names="value")

    def on_file_created(self, *args, **kwargs):
        return self.foa.on_file_create(*args, **kwargs)

    def tag_data(self, _, filename):
        # load the metadata from a yaml template
        with open(self.metadata_app.template_filename, "rb") as f:
            template_metadata = yaml.load(f, Loader=yaml.SafeLoader)

        metadata = self.update_metadata(metadata=template_metadata, filename=filename)

        outyaml = Path(filename).with_suffix(f"{self.foa.suffix}.yaml")

        with open(outyaml, "w", encoding="utf-8") as f:
            yaml.dump(metadata, f)

    def update_metadata(self, metadata, filename):
        if self._update_metadata:
            return self._update_metadata(metadata=metadata, filename=filename)

        metadata.setdefault(
            "time metadata", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        metadata.setdefault("filename", filename)
        if self._variable_metadata:
            for key, item in self.metadata_app.variable_metadata.items():
                metadata[key] = item
        return metadata


    def layout_metadata(self):
        return VBox(children=[field for field in self.metadata_app.metadata_text_fields])

    def layout_observer(self):
        return VBox(
            children=[self.metadata_app.dropdown_yaml, self.foa.observer_layout()]
        )

    def basic_gui(self):
        tab = widgets.Tab()
        tab.children = [self.layout_observer()]
        tab.titles = ["Observer"]
        with self.output:
            return tab

    def metadata_gui(self):
        tab = widgets.Tab()
        tab.children = [self.layout_observer(), self.layout_metadata()]
        tab.titles = ["Observer", "Variable Metadata"]

        with self.output:
            return tab

    def gui(self):
        if self.metadata_app.metadata_text_fields:
            return self.metadata_gui()
        with self.output:
            return self.basic_gui()
