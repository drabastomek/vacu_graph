# Vacuum plate characteristics extractor

**vacu_graph** is a simple, Python-based, windowed and self-contained app (that still 
can be started from CLI)that helps to extract data from vacuum tubes plate / current characteristics. 

It's intended to help extract a tube characteristic data (plate current curves) so 
they can be used to build better defined Spice models. 
**NOTE:** automatic Spice model estimation will be added in the
future.

## Build / install from source
To build the app, run the following command from the root folder

```bash
pyinstaller --onefile --windowed --name vacu_graph --paths=. vacu_graph/app.py 
```
The app will be available in the `dist` folder and should contain two versions: CLI executable, and
a self-contained executable.

## Installation
### Environment setup for CLI


## Using the app
Here's some basic steps to use the app; we will use a 12AX7 / ECC83 tube example here.

1. Load the image with the tube characteristics.

<img src="assets/1_load.png" alt="drawing" width="640"/>

2. Annotate the axes first to set up the resolution and parameters for each axis.
    1. Click on the Annotate axes button.

    <img src="assets/2_a_annotate.png" alt="drawing" width="600"/>

    2. Draw a line from the origin of the char to a characteristic point on the chart. In the example below, we drew a line from 0mA to 4mA for the plate current axis. In the modal that shows up select the axis and input the minimum and maximum values in the relevant fields.
    
    <img src="assets/2_b_annotate.png" alt="drawing" width="600"/>

> [!IMPORTANT]  
> If you draw a horizontal line and by accident forget to change the axis to `Plate voltage` 
> the tool will alert you about it and you'll need to click again on the Annotate axes, draw the 
> line and fill the information in the dialog window again.

Repeat the steps for the other axis.

3. For each curve repeat the following steps to annotate them.

    1. Draw small sections of the line on the canvas as close as you can to the curve you are
    annotating.

    <img src="assets/3_a_line.png" alt="drawing" width="600"/>

    2. Once done, click on Annotate line and in the dialog -- add the name for this line.

    <img src="assets/3_b_line.png" alt="drawing" width="600"/>

    3. If all successful, the added curve will appear in blue on the chart.

    <img src="assets/3_c_line.png" alt="drawing" width="600"/>

4. Finally, before you click the Save annotations button, fill in the Tube type and Voltage resolution
fields. 

> [!IMPORTANT]  
> Should you forget to do so -- the dialog will inform you that this needs to be done before you can 
> save the results. 

Upon clicking the Save annotations, the tool will ask you to selec the folder where to store the results
in; the folder will remain the same for the duration of the session. 

The tool will output two files

<img src="assets/4_b_save.png" alt="drawing" width="600"/>

The `{filename}-agg.csv` will contain the results aggregated at the selected resolution 
(e.g. every multiple of 10V or 5V for the plate voltage) and the corresponding current for each 
annotated curve. In contrast, the `{filename}-hi_res.csv` will contain all the results down to the 
pixel level if so you can aggregate them up at different resolution levels later.

## Contributing to `vacu_graph`

We welcome contributions to **vacu_graph** and appreciate your interest in improving the project! Contributions can take many forms, including reporting bugs, suggesting features, improving documentation, or submitting code.

## Types of Contributions

### 1. Reporting Issues or Requesting Features

To report a bug, request a new feature, or identify an issue with the documentation:

- Please [open an issue](https://github.com/your-username/vacu_graph/issues) on GitHub.
- Provide as much detail as possible, including steps to reproduce the issue or a clear description of the feature request.
- The **vacu_graph** team will triage and evaluate the issue. If you feel an issue is particularly urgent, you can comment on it to bring it to our attention.

### 2. Proposing and Implementing New Features

If you would like to propose a new feature:

- First, file a feature request as a GitHub issue.
- Describe the proposed feature and your intended approach to implementing it.
- Use the issue to start a discussion with the maintainers and community.
- Once there is agreement on the approach, you're welcome to start development. Follow the coding guidelines in the next section when submitting a pull request.

### 3. Fixing Bugs or Implementing Enhancements

If you're working on an issue that already exists:

- Let others know by commenting on the issue.
- If you need clarification, don't hesitate to ask in the comments.
- When you're ready, submit a pull request that references the issue number. Be sure your code adheres to the style and testing guidelines described in the code contributions section.

## Code Contributions

Coming soon: A detailed guide on how to set up your environment, run tests, and follow coding conventions for **vacu_graph**. In the meantime, please:

- Write clean, readable code.
- Include appropriate tests for new features or bug fixes.
- Document any public interfaces you add or modify.

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat others with respect and contribute in a way that fosters a welcoming and inclusive community.

---

Thank you for your contributions and support!