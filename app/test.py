import slugify


def extract_dataset(tables):
    dataset = {}
    for table in tables:
        for tbody in table.element.getchildren():
            for tr in tbody.getchildren():
                row = []
                for col in tr.getchildren():
                    content = ""
                    try:
                        content = col.text_content()
                    except Exception:
                        pass
                    if content != "":
                        _content = content.strip()
                        row.append(_content)
                    row.append(col.text_content())
                if len(row) != 2:
                    continue
                key = row[0]
                value = row[1]
                data = {}
                key = slugify(key)
                if key in dataset:
                    continue
                else:
                    dataset[key] = value
    return dataset
