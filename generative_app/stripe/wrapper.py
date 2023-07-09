paylink_html = """<body>
  <h1>Purchase your new kit</h1>
  <!-- Paste your embed code script here. -->
  <script
    async
    src="https://js.stripe.com/v3/buy-button.js">
  </script>
  <stripe-buy-button
    buy-button-id='{{BUY_BUTTON_ID}}'

    publishable-key=

"pk_test_51NRxMRGUJVa5kUSYzkzqua90epxkN1Le3sG0YmqHLjHb5ATQPh8jp0GeiRWeImyGUMN0eQujsVyizoEhE3hoIzY100YwJFYiJI"

  >
  </stripe-buy-button>
</body>"""