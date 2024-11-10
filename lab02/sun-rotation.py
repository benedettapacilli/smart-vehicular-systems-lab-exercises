import carla
import math
import datetime
import time

HOST = 'localhost'

class Sun:
    """Simulates sun position in the sky based on time of day."""
    def __init__(self):
        """Initialize sun position at zenith (directly overhead).

        Parameters:
            azimuth (float): Sun's horizontal position in degrees
            altitude (float): Sun's vertical position in degrees
        """
        self.azimuth = 0
        self.altitude = 0

    def calculate_position(self, hour):
        """Calculate sun position based on time of day.

        Simulates a realistic day-night cycle with:
        - Sunrise around 6 AM (hour 6)
        - Solar noon around 12 PM (hour 12)
        - Sunset around 6 PM (hour 18)

        Args:
            hour (float): Current time in 24-hour format
        """
        self.azimuth = ((hour - 6) * 15) % 360 # 15 degrees per hour

        time_rad = math.radians((hour - 6) * 15) # Convert to radians
        self.altitude = 70 * math.sin(time_rad) if 6 <= hour <= 18 else -20 # 70 degrees at solar noon

    def __str__(self):
        return f'Sun(alt: {self.altitude:.2f}, azm: {self.azimuth:.2f})'

class Weather:
    """Controls weather conditions including sun position and atmospheric effects."""
    def __init__(self, weather):
        """Initialize weather controller.

        Args:
            weather: CARLA weather object to control

        Parameters:
            weather (carla.WeatherParameters): Current weather conditions
            sun (Sun): Simulated sun position
            simulation_hours (float): Elapsed time in simulation hours
        """
        self.weather = weather
        self._sun = Sun()
        self.simulation_hours = 0

    def tick(self, delta_seconds):
        """Update weather conditions based on elapsed time.

        Updates sun position and atmospheric conditions. One real second
        equals 10 simulation minutes.

        Args:
            delta_seconds (float): Elapsed time since last update in seconds
        """
        self.simulation_hours = (self.simulation_hours + (delta_seconds * 10/60)) % 24

        self._sun.calculate_position(self.simulation_hours)

        self.weather.sun_azimuth_angle = self._sun.azimuth
        self.weather.sun_altitude_angle = self._sun.altitude

        self.weather.cloudiness = 0
        if 6 <= self.simulation_hours <= 18:
            self.weather.fog_density = 0
        else:
            self.weather.fog_density = 30

    def __str__(self):
        return f'{self._sun} Time: {int(self.simulation_hours):02d}:{int((self.simulation_hours % 1) * 60):02d}'

def main():
    client = carla.Client(HOST, 2000)
    client.set_timeout(15.0)
    world = client.get_world()

    spectator = world.get_spectator()
    transform = spectator.get_transform()
    transform.location = carla.Location(x=0, y=0, z=50)
    transform.rotation = carla.Rotation(pitch=-60)
    spectator.set_transform(transform)

    weather = Weather(world.get_weather())
    elapsed_time = 0.0

    try:
        while True:
            timestamp = world.wait_for_tick().timestamp
            elapsed_time += timestamp.delta_seconds
            weather.tick(elapsed_time)
            world.set_weather(weather.weather)
            print(f'\r{weather}', end='', flush=True)
            elapsed_time = 0.0
            time.sleep(0.1)  # Limit update rate

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")

if __name__ == '__main__':
    main()