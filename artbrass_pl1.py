import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_all_categories():
    # Dictionary with URLs and number of pages to scrape
    categories = {
        "https://theartofbrass.com/shop/": 5  # Adjust the number of pages as needed
    }
    
    all_product_data = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        
        for category_url, total_pages in categories.items():
            page = browser.new_page()

            for page_num in range(1, total_pages + 1):
                # Navigate to each page of the category with increased timeout and specific wait
                try:
                    page.goto(f"{category_url}page/{page_num}/", timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_selector("//div//a[@class ='woocommerce-LoopProduct-link woocommerce-loop-product__link']", timeout=20000)
                except Exception as e:
                    print(f"Failed to load category page {page_num} due to: {e}")
                    continue  # Move to the next page if this one fails

                # Get product links in the current category
                product_links = page.locator("//div//a[@class ='woocommerce-LoopProduct-link woocommerce-loop-product__link']")
                product_urls = [link.get_attribute('href') for link in product_links.element_handles()]

                # Iterate over each product link
                for product_url in product_urls:
                    try:
                        page.goto(product_url, timeout=60000, wait_until="domcontentloaded")
                        page.wait_for_selector("//h1", timeout=30000)

                        # Extract title
                        product_name = page.locator("//h1").text_content().strip() if page.locator("//h1").is_visible() else None

                        # Extract price
                        price = page.locator("//p//span[@class='woocommerce-Price-amount amount']").text_content().strip() if page.locator("//p//span[@class='woocommerce-Price-amount amount']").is_visible() else None

                        # Extract tags
                        tags = page.locator("//span[@class='tagged_as']").text_content().strip() if page.locator("//span[@class='tagged_as']").is_visible() else None

                        # Extract all <p> tags from the description
                        description_elements = page.locator("//div[@class='woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content wc-tab']/p")
                        description = " ".join([description_elements.nth(i).text_content().strip() for i in range(description_elements.count())])

                        # Extract image URL
                        img_url = page.locator("//div//img[@class='wp-post-image']").get_attribute("src") if page.locator("//div//img[@class='wp-post-image']").is_visible() else None

                        # Prepare the product data
                        product_data = {
                            "Title": product_name,
                            "Price": price,
                            "Tags": tags,
                            "Description": description,
                            "Image URL": img_url,
                            "Source URL": product_url
                        }

                        # Append product data to the list
                        all_product_data.append(product_data)

                    except Exception as e:
                        print(f"Failed to load {product_url}: {e}")
                        continue  # Skip to the next product on failure

            # Close the page after each category
            page.close()

        # Close the browser
        browser.close()

    # Create a DataFrame from the scraped data
    df = pd.DataFrame(all_product_data)

    # Save the DataFrame to a CSV file
    df.to_csv("the_art_of_brass_data.csv", index=False, encoding='utf-8-sig')
    print(df)

# Call the function to run the scraper
scrape_all_categories()
