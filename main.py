import streamlit as st

# Header
st.markdown("""
<div style="margin-bottom: 32px;">
    <span style="font-size:11px; letter-spacing:.15em;
           padding:4px 10px; border:1px solid #70d6f5;
          border-radius:4px; background-color:#ffff; color:#05c8eb;">CLAIM CHECK</span>
    <h1 style="font-weight:700; font-size:30px; color:#444444;
               line-height:1.2; margin-top:10px;">
        Does this seller deliver what they promise?
    </h1>
    <p style="color:#888; font-size:14px; margin-top:8px;">
        Paste a Jumia product URL. We compare what the seller claims
        against what customers actually say.
    </p>
</div>
""", unsafe_allow_html=True)


# Product URL input
url = st.text_input(label="Product URL", placeholder="https://www.jumia.com.ng/...", label_visibility="collapsed")


# Analyze button and info
col_btn, col_info = st.columns([1, 3])
with col_btn:
    analyze = st.button("Analyze →", use_container_width=True)
with col_info:
    st.markdown(
        '<p style="font-size:13px; font-weight:500; color: #7a7a7a; margin-top:10px;">Based on first 10 reviews</p>',
        unsafe_allow_html=True
    )


# spacing
st.write("\n")


# Analysis logic 
if analyze:
    if not url or not url.startswith("https://www.jumia.com.ng/"):
        st.error("Please enter a valid Jumia product URL.")
    else:
        with st.status(label="Running Analysis", expanded=True) as status:
            pass


# product_name = "Rice and beans"
# st.write(product_name)

# # Aspect Summary
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric(label="Aspect Checked", value="4", border=True)
# with col2:
#     st.metric(label="Confirmed", value="2", border=True)
# with col3:
#     st.metric(label="Conflicted/Disputed", value="2", border=True)


# for x in range(4):
#     with st.expander(f"Aspect {x+1}"):
#         st.write(f"Aspect {x+1}")
#         st.write("Claim: The product is fresh.")
#         st.write("Evidence: Customer reviews and photos confirm freshness.")
#         st.write("Status: Confirmed")

# def main():
#     print("Hello from claim-check!")


# if __name__ == "__main__":
#     main()
