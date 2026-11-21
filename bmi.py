class BMI:
    def __init__(self, weight, height):
        self.weight = weight
        self.height = height

    def calculate_bmi(self):
        return self.weight / (self.height ** 2)

    def show_result(self):
        bmi = self.calculate_bmi()
        print(f"Your BMI is: {bmi:.2f}")

        if bmi < 18.5:
            print("Status: Underweight")
        elif bmi < 25:
            print("Status: Normal weight")
        elif bmi < 30:
            print("Status: Overweight")
        else:
            print("Status: Obese")


def main():
    weight = float(input("Enter your weight in kilograms: "))
    height = float(input("Enter your height in meters: "))

    person = BMI(weight, height)
    person.show_result()


if __name__ == "__main__":
    main()
