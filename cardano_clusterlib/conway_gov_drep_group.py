"""Group of methods for Conway governance DRep commands."""
import logging
import pathlib as pl
import typing as tp

from cardano_clusterlib import clusterlib_helpers
from cardano_clusterlib import helpers
from cardano_clusterlib import structs
from cardano_clusterlib import types as itp


LOGGER = logging.getLogger(__name__)


class ConwayGovDrepGroup:
    def __init__(self, clusterlib_obj: "itp.ClusterLib") -> None:
        self._clusterlib_obj = clusterlib_obj
        self._group_args = ("governance", "drep")

    def _get_key_args(
        self,
        drep_vkey: str = "",
        drep_vkey_file: tp.Optional[itp.FileType] = None,
        drep_key_hash: str = "",
    ) -> tp.List[str]:
        """Get arguments for verification key."""
        if drep_vkey:
            key_args = ["--drep-verification-key", str(drep_vkey)]
        elif drep_vkey_file:
            key_args = ["--drep-verification-key-file", str(drep_vkey_file)]
        elif drep_key_hash:
            key_args = ["--drep-key-hash", str(drep_key_hash)]
        else:
            raise AssertionError(
                "Either `drep_vkey`, `drep_vkey_file` or `drep_key_hash` is needed."
            )

        return key_args

    def gen_key_pair(self, key_name: str, destination_dir: itp.FileType = ".") -> structs.KeyPair:
        """Generate DRep verification and signing keys.

        Args:
            key_name: A name of the key pair.
            destination_dir: A path to directory for storing artifacts (optional).

        Returns:
            structs.KeyPair: A tuple containing the key pair.
        """
        destination_dir = pl.Path(destination_dir).expanduser()
        vkey = destination_dir / f"{key_name}_drep.vkey"
        skey = destination_dir / f"{key_name}_drep.skey"
        clusterlib_helpers._check_files_exist(vkey, skey, clusterlib_obj=self._clusterlib_obj)

        self._clusterlib_obj.cli(
            [
                *self._group_args,
                "key-gen",
                "--verification-key-file",
                str(vkey),
                "--signing-key-file",
                str(skey),
            ]
        )

        helpers._check_outfiles(vkey, skey)
        return structs.KeyPair(vkey, skey)

    def gen_id(
        self,
        id_name: str,
        drep_vkey: str = "",
        drep_vkey_file: tp.Optional[itp.FileType] = None,
        out_format: str = "",
        destination_dir: itp.FileType = ".",
    ) -> str:
        """Generate a DRep id.

        Args:
            id_name: A name of payment address.
            drep_vkey: DRep verification key (Bech32 or hex-encoded, optional).
            drep_vkey_file: A path to corresponding drep vkey file (optional).
            out_format: Output format (optional, bech32 by default).
            destination_dir: A path to directory for storing artifacts (optional).

        Returns:
            str: A generated DRep id.
        """
        destination_dir = pl.Path(destination_dir).expanduser()
        out_file = destination_dir / f"{id_name}_drep.id"
        clusterlib_helpers._check_files_exist(out_file, clusterlib_obj=self._clusterlib_obj)

        if drep_vkey:
            cli_args = ["--drep-verification-key", str(drep_vkey)]
        elif drep_vkey_file:
            cli_args = ["--drep-verification-key-file", str(drep_vkey_file)]
        else:
            raise AssertionError("Either `drep_vkey` or `drep_vkey_file` is needed.")

        if out_format:
            cli_args.extend(["--output-format", str(out_format)])

        self._clusterlib_obj.cli(
            [
                *self._group_args,
                "id",
                *cli_args,
                "--out-file",
                str(out_file),
            ]
        )

        helpers._check_outfiles(out_file)
        return helpers.read_address_from_file(out_file)

    def gen_registration_cert(
        self,
        cert_name: str,
        deposit_amt: int,
        drep_vkey: str = "",
        drep_vkey_file: tp.Optional[itp.FileType] = None,
        drep_key_hash: str = "",
        drep_metadata_url: str = "",
        drep_metadata_hash: str = "",
        destination_dir: itp.FileType = ".",
    ) -> pl.Path:
        """Generate a DRep registration certificate.

        Args:
            cert_name: A name of the cert.
            deposit_amt: A key registration deposit amount.
            drep_vkey: DRep verification key (Bech32 or hex-encoded, optional).
            drep_vkey_file: Filepath of the DRep verification key (optional).
            drep_key_hash: DRep verification key hash
                (either Bech32-encoded or hex-encoded, optional).
            drep_metadata_url: URL to the metadata file (optional).
            drep_metadata_hash: Hash of the metadata file (optional).
            destination_dir: A path to directory for storing artifacts (optional).

        Returns:
            Path: A path to the generated certificate.
        """
        destination_dir = pl.Path(destination_dir).expanduser()
        out_file = destination_dir / f"{cert_name}_drep_reg.cert"
        clusterlib_helpers._check_files_exist(out_file, clusterlib_obj=self._clusterlib_obj)

        key_args = self._get_key_args(
            drep_vkey=drep_vkey,
            drep_vkey_file=drep_vkey_file,
            drep_key_hash=drep_key_hash,
        )

        metadata_args = []
        if drep_metadata_url:
            metadata_args = [
                "--drep-metadata-url",
                str(drep_metadata_url),
                "--drep-metadata-hash",
                str(drep_metadata_hash),
            ]

        self._clusterlib_obj.cli(
            [
                *self._group_args,
                "registration-certificate",
                *key_args,
                "--key-reg-deposit-amt",
                str(deposit_amt),
                *metadata_args,
                "--out-file",
                str(out_file),
            ]
        )

        helpers._check_outfiles(out_file)
        return out_file

    def gen_retirement_cert(
        self,
        cert_name: str,
        deposit_amt: int,
        drep_vkey: str = "",
        drep_vkey_file: tp.Optional[itp.FileType] = None,
        drep_key_hash: str = "",
        destination_dir: itp.FileType = ".",
    ) -> pl.Path:
        """Generate a DRep retirement certificate.

        Args:
            cert_name: A name of the cert.
            deposit_amt: A key registration deposit amount.
            drep_vkey: DRep verification key (Bech32 or hex-encoded, optional).
            drep_vkey_file: Filepath of the DRep verification key (optional).
            drep_key_hash: DRep verification key hash
                (either Bech32-encoded or hex-encoded, optional).
            destination_dir: A path to directory for storing artifacts (optional).

        Returns:
            Path: A path to the generated certificate.
        """
        destination_dir = pl.Path(destination_dir).expanduser()
        out_file = destination_dir / f"{cert_name}_drep_retirement.cert"
        clusterlib_helpers._check_files_exist(out_file, clusterlib_obj=self._clusterlib_obj)

        key_args = self._get_key_args(
            drep_vkey=drep_vkey,
            drep_vkey_file=drep_vkey_file,
            drep_key_hash=drep_key_hash,
        )

        self._clusterlib_obj.cli(
            [
                *self._group_args,
                "retirement-certificate",
                *key_args,
                "--deposit-amt",
                str(deposit_amt),
                "--out-file",
                str(out_file),
            ]
        )

        helpers._check_outfiles(out_file)
        return out_file

    def get_metadata_hash(
        self,
        drep_metadata_file: itp.FileType,
    ) -> str:
        """Get the hash of the metadata.

        Args:
            drep_metadata_file: A path to the metadata file.

        Returns:
            str: A hash of the metadata.
        """
        drep_metadata_file = pl.Path(drep_metadata_file).expanduser()
        clusterlib_helpers._check_files_exist(
            drep_metadata_file, clusterlib_obj=self._clusterlib_obj
        )

        metadata_hash = (
            self._clusterlib_obj.cli(
                [
                    *self._group_args,
                    "metadata-hash",
                    "--drep-metadata-file",
                    str(drep_metadata_file),
                ]
            )
            .stdout.rstrip()
            .decode("ascii")
        )

        return metadata_hash
