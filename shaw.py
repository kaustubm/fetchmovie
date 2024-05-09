import streamlit as st
import pandas as pd
from imdb import IMDb
import concurrent.futures

def get_movie_info_batch(titles):
    ia = IMDb()
    result = []
    for title in titles:
        movies = ia.search_movie(title)
        if movies:
            movie_id = movies[0].movieID
            movie = ia.get_movie(movie_id)
            country = movie.get('country', [''])[0]
            genre = ', '.join(movie.get('genres', ['']))
            result.append((country, genre))
        else:
            result.append(('', ''))
    return result

def main():
    st.title('Film Data Automation')
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write('**Original DataFrame**')
        st.write(df)

        # Process titles in batches using threading
        batch_size = 50
        num_batches = (len(df) + batch_size - 1) // batch_size
        progress_bar = st.progress(0)
        progress_text = st.empty()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = []
            for i in range(0, len(df), batch_size):
                batch_titles = df.iloc[i:i+batch_size]['Film Title']
                future = executor.submit(get_movie_info_batch, batch_titles)
                results.append(future)

            # Update DataFrame with results
            for i, future in enumerate(results):
                batch_results = future.result()
                for j, (country, genre) in enumerate(batch_results):
                    df.at[i*batch_size+j, 'Country of Origin'] = country
                    df.at[i*batch_size+j, 'Genre'] = genre

                # Update progress bar
                progress = (i + 1) / num_batches
                progress_bar.progress(progress)
                progress_text.text(f"Processing: {i + 1}/{num_batches} batches")

        st.write('**Modified DataFrame**')
        st.write(df)

        # Download modified Excel file
        output_file = 'output_excel_file.xlsx'
        df.to_excel(output_file, index=False)
        st.write(f"Download modified file [here](./{output_file})")

if __name__ == "__main__":
    main()

