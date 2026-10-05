import pandas as pd
import matplotlib.pyplot as plt
# ticker module calculates where ticks go (how numbers formatted on axes)
from matplotlib.ticker import MultipleLocator

class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):
        """
        Utility class used to monitor bioprocesses by
        generating dashboards and summaries.

        Parameters
        ----------
        filepath : str
            Input CSV dataset path.
        ph_lims : tuple[float, float]
            Lower and upper acceptable pH limits.
        temperature_lims : tuple[float, float]
            Lower and upper acceptable temperature limits.
        """
        #read dataset into pandas:
        self.df = pd.read_csv(filepath)
        # store pH and temp limit (acceptable ranges):
        self.ph_lims = ph_lims
        self.temperature_lims = temperature_lims

    def extract_batch(self, batch_id):
        """
        Extracts data corresponding to a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing only rows associated with
            the requested batch.
        """
        df_batch = self.df[self.df['batch_id'] == batch_id].copy()

        return df_batch

    def optimal_ph_mask(self, df_batch):
        """
        Determines whether each pH measurement falls within
        the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """
        #get lower and upper limits for pH
        lower_limit, upper_limit = self.ph_lims
        #return boolean series (True if within [lower_limit, upper_limit], False else
        return df_batch['pH'].between(lower_limit, upper_limit)


    def optimal_temperature_mask(self, df_batch):
        """
        Determines whether each temperature measurement falls
        within the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """
        # get lower and upper limits for temperature
        lower_limit, upper_limit = self.temperature_lims
        # return boolean series (True if within [lower_limit, upper_limit], False else
        return df_batch['temperature_C'].between(lower_limit, upper_limit)

    def get_n_batches(self):
        """
        Determines the number of unique batches present
        in the dataset.

        Returns
        -------
        int
            Total number of distinct batch identifiers.
        """
        #count the unique batch IDs in the dataset
        return self.df['batch_id'].nunique()

    def export_dashboard(self, batch_id, filepath):

        """
        Creates and saves a dashboard figure for a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.
        filepath : str
            Output PNG image path.

        Dashboard Requirements
        ----------------------
        Create a 2 × 2 figure containing:

        Top-Left
            Glucose, biomass, and product concentrations versus time.
            - A different color and marker should be used for each substance.

        Top-Right
            Temperature versus time.
            - Measurements within the acceptable temperature range
              should be displayed as green circles.
            - Measurements outside the acceptable temperature range
              should be displayed as red X markers.

        Bottom-Left
            pH versus time.
            - Measurements within the acceptable pH range
              should be displayed as green circles.
            - Measurements outside the acceptable pH range
              should be displayed as red X markers.

        Bottom-Right
            Dissolved oxygen versus time.

        Additional Requirements
        -----------------------
        - Use scatter plots.
        - Add x-axis and y-axis labels.
        - Add legends where appropriate.
        - Apply consistent formatting across all subplots unless
          indicated otherwise.
        - Apply a tick spacing of 6 h on the x-axis for all subplots.
        - Save the figure to the provided filepath.
        - Close the figure after saving.
        """
       #extract data for the given batch ID
        df_batch = self.extract_batch(batch_id)
        # check which temperature and pH are within the limits (acceptable ranges)
        ph_ok = self.optimal_ph_mask(df_batch)
        temp_ok = self.optimal_temperature_mask(df_batch)
        #create 2x2 figure (fig = dashboard, axes = four individual graph spaces/subplots)
        fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=200, layout="constrained")

    #___________
    # Subplot 1! (Top-Left): Glucose, Biomass, Product vs. Time
    # ___________
        ax1 = axes[0,0]
        ax1.scatter(df_batch["time_h"], df_batch["C_glucose_g_L^-1"], color="blue", marker="*", edgecolors="black", linewidth=0.5, label="Glucose")
        ax1.scatter(df_batch["time_h"], df_batch["C_product_g_L^-1"], color="orange", marker="^", edgecolors="black", linewidth=0.5, label="Product")
        ax1.scatter(df_batch["time_h"], df_batch["C_biomass_g_L^-1"], color="purple", marker="o", edgecolors="black", linewidth=0.5, label="Biomass")
        ax1.set_title("Concentrations vs Time")
        ax1.set_xlabel("Time (h)")
        ax1.set_ylabel("Concentration [g/L]")
        ax1.legend()

    # ___________
    # Subplot 2! (Top-Right): Temp vs. Time
    # ___________
        ax2 = axes[0,1]
        ax2.scatter(df_batch["time_h"][temp_ok], df_batch["temperature_C"][temp_ok], color="green", marker="o", edgecolors="black", linewidth=0.5, label="Optimal")
        ax2.scatter(df_batch["time_h"][~temp_ok], df_batch["temperature_C"][~temp_ok], color="red", marker="x", label="Sub-Optimal")
        ax2.set_title("Temperature vs Time")
        ax2.set_xlabel("Time (h)")
        ax2.set_ylabel("Temperature (°C)")
        ax2.legend()

    # ___________
    # Subplot 3! (Bottom-Left): pH vs. Time
    # ___________
        ax3 = axes[1,0]
        ax3.scatter(df_batch["time_h"][ph_ok], df_batch["pH"][ph_ok], color="green", marker="o", edgecolors="black", linewidth=0.5, label="Optimal")
        ax3.scatter(df_batch["time_h"][~ph_ok], df_batch["pH"][~ph_ok], color="red", marker="x", label="Sub-Optimal")
        ax3.set_title("pH vs Time")
        ax3.set_xlabel("Time (h)")
        ax3.set_ylabel("pH")
        ax3.legend()

    # ___________
    # Subplot 4! (Bottom-Right): Dissolved Oxygen (DO) [%] vs Time
    # ___________
        ax4 = axes[1,1]
        ax4.scatter(df_batch["time_h"], df_batch["DO_percent"], color="magenta", edgecolors="black", linewidth=0.5, marker="D")
        ax4.set_title("Dissolved Oxygen vs Time")
        ax4.set_xlabel("Time (h)")
        ax4.set_ylabel("Dissolved Oxygen [%]")

    #Formatting: Set 6hr ticks on x-axis for all plots, save and close
        for ax in axes.flat:
            ax.xaxis.set_major_locator(MultipleLocator(6))
            #Taken from notes: unit_03 and added gridlines
            ax.tick_params(axis="both", which="major", labelsize=10)
            ax.grid(True, linestyle="--", alpha=0.5)
            #Save and close
        fig.savefig(filepath, dpi=200)
        plt.close(fig)

    def export_summary(self, filepath):
        """
        Generates a batch summary table and exports it to a CSV file.

        Parameters
        ----------
        filepath : str
            Output CSV table path.

        Summary Table Columns
        ---------------------
        batch_id
            Batch identifier.

        ph_optimal_percent
            Percentage of measurements in a batch within the
            acceptable pH range, rounded to 2 decimal places.

        temperature_optimal_percent
            Percentage of measurements in a batch within the
            acceptable temperature range, rounded to 2 decimal places.

        C_product_g_L^-1_final
            Final product concentration for the batch.
        """

        #create empty list to store all summary information
        summary = []
        for batch_id in range(1, self.get_n_batches() + 1):
            #get data for this batch
            df_batch = self.extract_batch(batch_id)

            #check measurements are in acceptable ranges
            ph_ok = self.optimal_ph_mask(df_batch)
            temp_ok = self.optimal_temperature_mask(df_batch)
            #calculate percentages of pH and temps being within the acceptable ranges
            ph_pct = round((ph_ok.sum() / len(df_batch)) * 100, 2)
            temp_pct = round((temp_ok.sum() / len(df_batch)) * 100, 2)

            #get final product concentration
            final_product = df_batch["C_product_g_L^-1"].iloc[-1]

            #add results of this batch to the summary
            summary.append({
                "batch_id": batch_id,
                "ph_optimal_percent": ph_pct,
                "temperature_optimal_percent": temp_pct,
                "C_product_g_L^-1_final": final_product
            })

    #create Dataframe with summary info
            summary_df = pd.DataFrame(summary)

    #export to CSV file
            summary_df.to_csv(filepath, index=False)

