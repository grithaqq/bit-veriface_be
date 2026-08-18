from shared import entity


def paginate_data(total, skip, limit):
    # Calculate page number
    page_number = (skip // limit) + 1

    # Calculate total pages
    total_pages = total // limit
    if total % limit != 0:
        total_pages += 1

    return entity.Pagination(
        total_item=total,
        total_page=total_pages,
        page_size=limit,
        curr_page=page_number,
        prev_page=page_number - 1 if page_number > 1 else 0,
        next_page=page_number + 1 if page_number < total_pages else 0,
        has_prev=page_number > 1,
        has_next=page_number < total_pages,
    )
