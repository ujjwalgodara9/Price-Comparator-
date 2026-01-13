async function searchDmart(query, page = 1, size = 40, storeId = 10706) {
  const url = `https://digital.dmart.in/api/v3/search/${encodeURIComponent(query)}?page=${page}&size=${size}&channel=web&searchTerm=${encodeURIComponent(query)}&storeId=${storeId}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "X-REQUEST-ID": "ODdkN2I4MDAtMzU0Ni00Mjk0LThhZjgtODA0YjE2NWE2NjI4fHxTLTIwMjYwMTA2XzE1NDgyMnx8LTEwMDI=",
      "storeId": storeId.toString(),
      "d_info": "w-20260106_154822",
      "Content-Type": "application/json;charset=UTF-8",
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }
  });

  if (!response.ok) {
    throw new Error(`DMart API error: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

const ab = await searchDmart('peanut butter')
console.log("(ABA)", ab)