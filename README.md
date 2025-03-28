# APW Math Assist v2

This project is a Python application that integrates mathematical problem-solving with serial communication. It uses the OpenAI API to generate reasoning steps and suggestions for math problems. Additionally, it reads data from a serial port to update the user's psychological state.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Setup Instructions

### Step 1: Create a Virtual Environment

1. Open a command prompt.
2. Navigate to the project directory:
   ```bash
   cd g:\_BadoCode\APW_Math_Assist
   ```

3. Create a virtual environment named `venv`:
   ```bash
   python -m venv venv
   ```

### Step 2: Activate the Virtual Environment

- On Windows:
  ```bash
  venv\Scripts\activate
  ```

### Step 3: Install Required Libraries

Once the virtual environment is activated, install the necessary libraries using pip:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, you can install the libraries manually:

```bash
pip install tkinter
pip install pyserial
pip install openai
```

### Step 4: Run the Application

With the virtual environment activated and libraries installed, you can run the script:

```bash
python APW_Math_Assist-v2.py
```

## Usage

- Enter your OpenAI API key in the provided field.
- Describe the math problem in the text area and click "Generate Reasoning Steps" to get a structured reasoning.
- Enter a suggestion request and a label (0-6) to receive targeted hints.
- Connect to a serial port to start reading data and update the label field.

## Sleep Buster Device

The serial data used in this application is sourced from the "Sleep Buster" device. Sleep Buster is a system designed to capture signs of drowsy driving using the detection sensor APW and warn the driver. Released in February 2012, this product was jointly developed by the Prediction of Sleep Research Group and commercialized by Delta Tooling, Co., Ltd. It received a Minister's Award from the Ministry of Land, Infrastructure, Transport and Tourism at the Merit Award of the Industry-Academia-Government Collaboration 2010.

Sleep Buster captures the Aortic Pulse Wave (APW) occurring in a driver's upper body via a sensor on the car seat. It assesses the driver's fatigue state across 6 levels through fluctuation analysis of the APW. The system warns against changes in concentration or sudden changes in physical condition, such as hypnagogic signs, using a display and sounds to encourage the driver to take a break or nap.

**Supported Version:** 2.2.0.1E

## Judgment Mapping

The value returned by the Sleep Buster device corresponds to a judgment on the monitored subject's psychophysical conditions, represented by an integer between 1 and 11. Users are encouraged to edit the label mapping function according to their preferences, as the current implementation is only demonstrative.

## Troubleshooting

- If you encounter issues with serial communication, verify that the correct port is specified and that the device is connected.
- For API-related errors, ensure that your API key is valid and has sufficient permissions.
