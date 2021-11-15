import React, { useContext, useState } from 'react'
import { CircularProgress } from '@material-ui/core'
import Snackbar from '@material-ui/core/Snackbar';
import { ConfigStoreContext } from '../../store/stores'

const BibEntry = ({setJsonURL, setBibtexOpen, setBibtex, bibtex}) => {
  const [bibdata, setbibdata] = useState(bibtex || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)
  const configStore = useContext(ConfigStoreContext);
  console.log(configStore.apiUrl)
  const submitBibtex = async () => {
    setLoading(true)
    fetch(configStore.apiUrl,{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({'bibtex': bibdata }),
      mode: 'cors',
    }).then(response => response.json())
      .then(data => {
        setBibtex(bibdata)
        setJsonURL(data.jsonUrl)
        setBibtexOpen(false)
      }).catch(e => {
        setLoading(false)
        setError(true)
    })

  }
  return (
    <>
      <Snackbar
        open={error}
        autoHideDuration={2000}
        message="Something went wrong"
        style={{zIndex:'9999999999999'}}
        onClose={() => setError(false)}
      />
      {loading && (
        <CircularProgress style={{position:'absolute', zIndex:'9999999999', left:'50%',top:'50%'}}/>

      )}
      <textarea autoFocus value={bibdata} onChange={(e) => !loading && setbibdata(e.target.value)}  onKeyDown={(e) => {
        if((e.shiftKey && e.keyCode === 13)) {
          submitBibtex()
        }
      }} placeholder="paste your bibtext here then submit with shift + enter" style={{zIndex:'99999', width:'100%',height:'100%',background:'black', color: !loading ? '#fff': '#8a8a8a', position:'absolute','::focus': { 'outline': 'none' }, border:'1px solid black', resize:'none' }}></textarea>
      </>

  )
}

export default BibEntry