/** @type {import('tailwindcss').Config} */
// src/**/*.{vue,js,ts,jsx,tsx}
// this is taliwnd3 config file. In this project we use tailwind 4th version that doesn't support this configuration anymore. Soon we'll have to get rid of this file probably since it absolutely useless.
module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  plugins: [require('@headlessui/tailwindcss')],
  safelist: [
    {
      pattern: /grid-cols-\d{1,2}/,
    },
  ],
  theme: {
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
    },
    spacing: {
      sm: '2px',
      md: '4px',
      lg: '8px',
      xl: '16px',
      '2xl': '24px',
      '3xl': '36px',
      '4xl': '48px',
      0: '0px',
      0.5: '4px',
      1: '8px',
      2: '12px',
      3: '16px',
      4: '24px',
      5: '32px',
      6: '48px',
      10: '10px',
      20: '20px',
      25: '25px',
      30: '30px',
      35: '35px',
      40: '40px',
      45: '45px',
      50: '50px',
      70: '70px',
      80: '80px',
      100: '100px',
      110: '110px',
      120: '120px',
      132: '132px',
      140: '140px',
      142: '142px',
      145: '145px',
      150: '150px',
      180: '180px',
      188: '188px',
      198: '198px',
      200: '200px',
      215: '215px',
      218: '218px',
      245: '245px',
      275: '275px',
      290: '290px',
      305: '305px',
    },
    extend: {
      boxShadow: {
        xl: '0px 0px 14px 0px #999',
      },
      borderRadius: {
        theme: '8px',
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '16px',
      },
      colors: {
        blue: {
          100: '#6486FF',
          200: '#4A72FF',
          300: '#3260FF',
          400: '#1B4EFF',
          500: '#0039FF',
        },
        green: {
          100: '#62FF71',
          200: '#41E051',
          300: '#28D139',
          400: '#16BE27',
          500: '#00AE11',
        },
        pink: {
          100: '#FF68A7',
          200: '#F04A90',
          300: '#E72E7B',
          400: '#D71667',
          500: '#CE0057',
        },
        purple: {
          100: '#A768FF',
          200: '#964BFF',
          300: '#8934FF',
          400: '#7B1DFF',
          500: '#6A00FF',
        },
        orange: {
          100: '#FF8E67',
          200: '#FF794E',
          300: '#FF6835',
          400: '#E84E1B',
          500: '#C63F10',
        },
        teal: {
          100: '#63CEFF',
          200: '#4DC7FF',
          300: '#31BEFF',
          400: '#16A1E0',
          500: '#028ECE',
        },
        red: {
          100: '#FF6666',
          200: '#F24D4D',
          300: '#E22F2F',
          400: '#CF1818',
          500: '#B50101',
        },
        yellow: {
          100: '#FFDE7E',
          200: '#FFD557',
          300: '#FFCB32',
          400: '#E7B116',
          500: '#D7A000',
        },
        bronze: {
          100: '#E99F61',
          200: '#DB8842',
          300: '#C97228',
          400: '#B45C11',
          500: '#9A4700',
        },
        turquoise: {
          100: '#65FFE8',
          200: '#4BF0D7',
          300: '#30E9CD',
          400: '#12C9AD',
          500: '#00B79A',
        },
        gray: {
          100: '#F5F6F7',
          200: '#ADB8CC',
          300: '#6B7A99',
          400: '#EDEFF2',
          500: '#FAFBFC',
          600: '#F2F3F5',
        },
      },

      fontSize: {
        xs: '10px',
        sm: '12px',
        md: '14px',
        lg: '16px',
        xl: '18px',
        '2xl': '24px',
        '3xl': '30px',
        '4xl': '40px',
      },
      fontFamily: {
        roboto: ['Roboto', 'sans-serif'],
        sans: ['Poppins', 'sans-serif'],
        mono: ['Azeret Mono', 'ui-monospace'],
      },
    },
  },
  plugins: [],
}
