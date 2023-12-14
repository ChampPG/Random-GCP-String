import time
import secrets
from numpy import interp
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import pandas as pd
from scipy.stats import entropy


class GcpDot:
    """ GcpDot class for scraping GCP Dot data """
    def __init__(self, Firefox_path):
        """ Initialize GcpDot class with path to Firefox driver
        
            Firefox_path: string, path to Firefox driver
            
            Returns: None
        """

        self.drive_executable = Firefox_path
        self.stats = []

    def _run_headless_driver(self):
        """ Runs a headless Firefox driver to scrape GCP Dot data 
            
            Returns: float between 0.0 and 1.0
        """
        high = 0
        delay = 3

        driver = webdriver.Firefox(executable_path=self.drive_executable)

        driver.implicitly_wait(delay)
        driver.get("https://gcpdot.com/gcpchart.php")

        try:
            time.sleep(1)
            chart_height = driver.find_element_by_id('gcpChartShadow').get_attribute("height")
            dot = driver.find_elements_by_tag_name('div')[-1]
            dot_id = dot.get_attribute('id')
            time.sleep(1)
            dot_height = driver.find_element_by_id(dot_id).value_of_css_property('top')
            dot_height = dot_height.replace('px', '')

            print("Chart height: " + str(chart_height))
            print("Dot height: " + str(dot_height))

            # If dot height is greater than chart height, we've hit the bottom of the chart

            if (dot_height > chart_height):
                driver.close()
                return self._run_headless_driver()

            # Convert dot height to a float between 0.0 and 1.0 
            high = interp(float(dot_height), [0, float(chart_height)], [0.0, 1.0])

            
            if (len(str(high)) > 3):
                shift = float("0."+str(high)[3:])
            else:
                shift = high
            
            stat_dict = {"dot_height_raw": float(dot_height), "gcp_index": high, "ts": time.time(), "color":self._color_switch(high), "gcp_index_shifted": shift }
            self.stats.append(stat_dict)

        except (TimeoutException, Exception) as e:
            print("Sick exception: " + str(e))
            raise e
            
        driver.close()
        return high

    def _generate_gradient(self, colour1, colour2, width, height):
        """ Generates a gradient between two colours, returns a PIL Image object 
        
            colour1: RGB tuple
            colour2: RGB tuple
            width: int
            height: int
            
            Returns: PIL Image object
        """

        base = Image.new('RGB', (width, height), colour1)
        top = Image.new('RGB', (width, height), colour2)
        mask = Image.new('L', (width, height))
        mask_data = []

        ''' Gradient happens here, simple linear from top to bottom '''
        for y in range(height):
            for x in range(width):
                mask_data.append(int(255 * (y / height)))

        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        base.show()
        base.close()


    def _color_switch(self, high):
        """ Returns a color based on the GCP Index
        
            high: float between 0.0 and 1.0
            
            Returns: string of the color name
        """

        if (high == 0):
            color = "gray"
        elif (high < 0.05):
            color = "red"
        elif (high >= 0.05 and high < 0.10):
            color = "orange"
        elif (high >= 0.10 and high < 0.40):
            color = "yellow"
        elif (high >= 0.40 and high < 0.90):
            color = "green"
        elif (high >= 0.90 and high <= 0.95):
            color = "teal"
        elif (high >= 0.95 and high <= 1.0):
            color = "blue"
        else:
            color = "gray"

        return color

    def _get_entropy(self, labels, length=4):
        """ Calculates the entropy of a list of labels
        
            labels: list of labels
            length: int, length of the label to use for entropy calculation
            
            Returns: float, entropy of the list
        """

        pd_series = pd.Series(labels)
        counts = pd_series.value_counts()
        ent = entropy(counts)

        print("Entropy stats")
        print("Shannon Entropy: " + str(ent))

    def sample(self):
        """ Sample the GCP Dot and return the GCP Index 
        
            Returns: float between 0.0 and 1.0
        """

        high = self._run_headless_driver()
        return self.stats[-1]

    def random(self, new=True):
        """ Returns a random GCP Index from the stats list
        
            new: bool, if True, sample a new GCP Index, if False, return a random one from the stats list
        """

        if new:
            num = self.sample()
        else:
            if (len(self.stats) < 1):
                self.random(new=True)
            num = secrets.choice(self.stats)

        return num["gcp_index_shifted"]
        
    def gather(self, limit=420, mod=5, sleep=3, output=True):
        """ Gather GCP Index data
        
            limit: int, number of samples to gather
            mod: int, number of samples to gather before printing output
            sleep: int, number of seconds to sleep between samples
            output: bool, if True, print output to console
            
            Returns: None
        """
        
        while (limit > 0): 
            
            self.sample()
            time.sleep(sleep)

            if ((len(self.stats) % mod == 0) and output):
                for item in self.stats:
                    print(str(item["gcp_index_shifted"]))

if __name__ == "__main__":
    
    g = GcpDot()
    print(g.random())